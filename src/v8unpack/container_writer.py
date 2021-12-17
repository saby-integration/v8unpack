# -*- coding: utf-8 -*-
import datetime
import io
import os
import tempfile
import zlib
from base64 import b64encode
from hashlib import sha1
from struct import pack, calcsize

from . import helper
from .json_container_decoder import JsonContainerDecoder

# INT32_MAX
END_MARKER = 2147483647
DEFAULT_BLOCK_SIZE = 512  # 0x200
# Для формата старше 8.3.15
DEFAULT_BLOCK_SIZE64 = 65536  # 0x1000
# Размер буффера передачи данных из потока в поток
BUFFER_CHUNK_SIZE = 512


def epoch2int(epoch_time):
    """
    Преобразует время в формате "количество секунд с начала эпохи" в количество сотых микросекундных интервалов
    с 0001.01.01

    :param epoch_time: время в формате Python
    :type epoch_time: real
    :return: количество сотых микросекундных интервалов
    :rtype: int
    """
    # Начало эпохи на разных системах - разная дата
    # Поэтому явно вычисляем разницу между указанной датой и 0001.01.01
    return (datetime.datetime.fromtimestamp(epoch_time) - datetime.datetime(1, 1, 1)) // datetime.timedelta(
        microseconds=100)


def int2hex(value):
    """
    Получает строковое представление целого числа в шестнадцатиричном формате длиной не менее 4 байт

    :param value: конвертируемое число
    :type value: int
    :return: предоставление числа
    :type: string
    """
    return '{:02x}'.format(value).rjust(8, '0')


def get_size(file):
    """
    Возвращает размер file-like объекта

    :param file: объекта файла
    :type file: BufferedReader
    :return: размер в байтах
    :rtype: int
    """
    pos = file.tell()
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(pos)
    return size


class ContainerWriter(object):
    """
    Класс для записи контейнеров

    :param file: объект файла контейнера
    :type file: BufferedReader
    """

    def __init__(self, file):
        self.file = file
        self.toc = []

    def write_header(self):
        """
        Записывает заголовок контейнера

        """
        self.file.write(pack('4i', END_MARKER, DEFAULT_BLOCK_SIZE, 0, 0))

    def write_block(self, data, **kwargs):
        """
        Записывает блок данных в контейнер

        :param data: file-like объект
        :param kwargs: Опциональные параметры
        :return: смещение записанных данных (байт)
        :rtype: int
        """
        # размер данных блока
        size = kwargs.pop('size', get_size(data))
        offset = kwargs.pop('offset', get_size(self.file))
        self.file.seek(offset)

        block_size = kwargs.pop('block_size', max(DEFAULT_BLOCK_SIZE, size))
        next_block_offset = kwargs.pop('next_block_offset', END_MARKER)

        if len(kwargs) > 0:
            raise ValueError('Unsupported arguments: {}'.format(','.join(kwargs.keys())))

        header_data = ('\r\n', int2hex(size), ' ', int2hex(block_size), ' ', int2hex(next_block_offset), ' \r\n')
        header = pack('2s8ss8ss8s3s', *[x.encode() for x in header_data])

        self.file.write(header)
        self.write_block_data(self, data, self.file)

        self.file.write(b'\x00' * (block_size - data.tell()))

        return offset

    @staticmethod
    def write_block_data(container, data, dest_file):
        data.seek(0)
        while True:
            buffer = data.read(BUFFER_CHUNK_SIZE)
            if not buffer:
                break
            dest_file.write(buffer)

    def add_file(self, fd, name, inflate=False):
        """
        Добавляет файл в контейнер

        :param fd: file-like объект файла
        :type fd: BufferedReader
        :param name: Имя файла в контейнере
        :type name: string
        :param inflate: флаг сжатия
        :type inflate: bool
        """
        modify_time = epoch2int(os.stat(fd.fileno()).st_mtime)
        # В *nix это не время создания файла.
        creation_time = epoch2int(os.stat(fd.fileno()).st_ctime)

        buffer = b''.join([pack('QQi', creation_time, modify_time, 0), name.encode('utf-16-le'), b'\x00' * 4])
        attribute_doc_offset = self.write_block(io.BytesIO(buffer), block_size=len(buffer))

        if inflate:
            data_doc_offset = self.compress(self, fd, self.file, self.write_block)
        else:
            data_doc_offset = self.write_block(fd)

        self.toc.append((attribute_doc_offset, data_doc_offset))

    @staticmethod
    def compress(container, src_fd, dest_fd, block_writer):
        with tempfile.TemporaryFile() as f:
            compressor = zlib.compressobj(wbits=-15)
            src_fd.seek(0)
            while True:
                chunk = src_fd.read(BUFFER_CHUNK_SIZE)
                if not chunk:
                    f.write(compressor.flush())
                    break
                f.write(compressor.compress(chunk))
            data_doc_offset = block_writer(container, f, dest_fd)
        return data_doc_offset

    def write_toc(self):
        """
        Записывает оглавление контейнера
        """
        if len(self.toc) == 0:
            raise IOError('Container is empty')
        with tempfile.TemporaryFile() as f:
            for attr_offset, data_offset in self.toc:
                f.write(b''.join([pack('3i', attr_offset, data_offset, END_MARKER)]))

            size = get_size(f)
            total_blocks = size // DEFAULT_BLOCK_SIZE + 1

            if total_blocks == 1:
                self.write_block(f, size=size, offset=calcsize('4i'))
            else:
                f.seek(0)
                next_block_offset = get_size(self.file)
                self.write_block(io.BytesIO(f.read(DEFAULT_BLOCK_SIZE)), size=size, offset=calcsize('4i'),
                                 next_block_offset=next_block_offset, block_size=DEFAULT_BLOCK_SIZE)
                for i in range(1, total_blocks):
                    # 31 - длина заголовка блока
                    next_block_offset += DEFAULT_BLOCK_SIZE + 31
                    self.write_block(io.BytesIO(f.read(DEFAULT_BLOCK_SIZE)), size=0,
                                     next_block_offset=next_block_offset)
                self.write_block(io.BytesIO(f.read(DEFAULT_BLOCK_SIZE)), size=0)

    def __enter__(self):
        """
        Вход в блок. Позволяет применять оператор with.
        """
        self.write_header()
        self.file.write(b'\x00' * (DEFAULT_BLOCK_SIZE + 31))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Выход из блока. Позволяет применять оператор with.
        """
        self.write_toc()


def add_entries(container, folder, nested=False):
    """
    Рекурсивно добавляет файлы из директории в контейнер

    :param container: объект файла контейнера
    :type container: BufferedReader
    :param folder: каталог файлов, которые надо поместить в контейнер
    :type folder: string
    :param nested: обрабатывать вложенные каталоги
    :type nested: bool
    """
    entries = sorted(os.listdir(folder))
    for entry in entries:
        entry_path = os.path.join(folder, entry)
        if os.path.isdir(entry_path):
            with tempfile.TemporaryFile() as tmp:
                with ContainerWriter(tmp) as nested_container:
                    add_entries(nested_container, entry_path, nested=True)
                container.add_file(tmp, entry, inflate=not nested)
        else:
            with open(entry_path, 'rb') as entry_file:
                container.add_file(entry_file, entry, inflate=not nested)


def build(folder, filename, nested=False):
    """
    Запаковывает каталог в контейнер включая вложенные каталоги.
    Сахар для ContainerWriter.

    :param folder: каталог с данными, запаковываемыми в контейнер
    :type folder: string
    :param filename: имя файла контейнера
    :type filename: string
    """
    with open(filename, 'w+b') as f, ContainerWriter(f) as container:
        add_entries(container, folder, nested)


def calc_sha1(src_folder, dest_folder):
    entries = sorted(os.listdir(dest_folder))
    versions = []
    versions_file = ''
    for filename in entries:
        dest_path = os.path.join(dest_folder, filename)
        if filename == 'configinfo':
            versions_file = 'configinfo'
            continue

        with open(dest_path, 'rb') as file:
            data = file.read()
        versions.append(f'"{filename}"')
        versions.append(b64encode(sha1(data).digest()).decode())
    if not versions_file:
        return
    versions.insert(0, str(int(len(versions) / 2)))
    _versions = JsonContainerDecoder().encode_root_object([versions])

    src_path = os.path.join(src_folder, versions_file)
    dest_path = os.path.join(dest_folder, versions_file)

    with open(src_path, 'r+', encoding='utf-8') as file:
        data = file.read()
        data = data.replace('{____versions____}', _versions)
        file.seek(0)
        file.write(data)

    compress_and_build_simple_file(src_path, dest_path)
    pass


def compress_and_build_simple_file(src_path, dest_path):
    with open(dest_path, 'w+b') as dest_fd:
        with open(src_path, 'rb') as src_fd:
            ContainerWriter.compress(None, src_fd, dest_fd, ContainerWriter.write_block_data)


def compress_and_build(src_folder, dest_folder, *, pool=None, nested=False):
    helper.clear_dir(dest_folder)
    entries = sorted(os.listdir(src_folder))

    for filename in entries:
        src_path = os.path.join(src_folder, filename)
        dest_path = os.path.join(dest_folder, filename)
        # add_entry(container, src_folder, filename)
        if os.path.isdir(src_path):
            with open(dest_path, 'w+b') as dest_fd:
                with tempfile.TemporaryFile() as tmp:
                    with ContainerWriter(tmp) as nested_container:
                        add_entries(nested_container, src_path, nested=True)
                    ContainerWriter.compress(None, tmp, dest_fd, ContainerWriter.write_block_data)
        else:
            compress_and_build_simple_file(src_path, dest_path)
    calc_sha1(src_folder, dest_folder)
