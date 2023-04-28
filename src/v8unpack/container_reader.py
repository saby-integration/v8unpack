# -*- coding: utf-8 -*-
import os
import zlib
from datetime import datetime

from . import helper
from .container import Container, Container64
from .ext_exception import ExtException


class ContainerReader(object):
    """
    Класс для чтения контейнеров
    """

    def __init__(self, file, container=None):
        if container is None:
            self.container = Container64
        else:
            self.container = container
        try:
            header = self.container.read_header(file)
        except Exception as err:
            if self.container == Container64:
                self.container = Container
                header = self.container.read_header(file)
            else:
                raise err from err

        if header.default_block_size == 0:
            raise BufferError('Container is empty')

        self.file = file
        self.first_empty_block_offset = header.first_empty_block_offset
        self.default_block_size = header.default_block_size
        #: Список файлов в контейнере
        self.entries = self.container.read_entries(self.file)

    def extract(self, path, deflate=False, recursive=False):
        """
        Распаковывает содержимое контейнера в каталог

        :param path: каталог распаковки
        :type path: string
        :param deflate: разархивировать содержимое файлов
        :type deflate: bool
        :param recursive: выполнять рекурсивно
        :type recursive: bool
        """
        helper.clear_dir(path)
        if not self.entries:
            print('Пустой контейнер = распаковывать нечего')
            return

        for filename, file_obj in self.entries.items():
            self.extract_file(filename, file_obj, path, deflate, recursive)

    def extract_file(self, filename, file_obj, path, deflate=False, recursive=False):
        file_path = os.path.join(path, filename)
        with open(file_path, 'wb') as f:
            if deflate:
                # wbits = -15 т.к. у архивированных файлов нет заголовков
                decompressor = zlib.decompressobj(-15)
                for chunk in file_obj.data:
                    decomressed_chunk = decompressor.decompress(chunk)
                    f.write(decomressed_chunk)
            else:
                for chunk in file_obj.data:
                    f.write(chunk)

        if not recursive:
            return

        # Каждый файл внутри контейнера может быть контейнером
        # Для проверки является ли файл контейнером проверим первые 4 бита
        # Способ проверки ненадежный - нужно придумать что-то другое
        file_is_container = False
        with open(file_path, 'rb') as f:
            if f.read(4) == b'\xFF\xFF\xFF\x7F':
                file_is_container = True
        if file_is_container:
            temp_name = file_path + '.tmp'
            os.rename(file_path, temp_name)
            with open(temp_name, 'rb') as f:
                ContainerReader(f, container=self.container).extract(file_path, recursive=True)
            os.remove(temp_name)


def extract(filename, folder, deflate=True, recursive=True):
    """
    Распаковка контейнера. Сахар для ContainerReader

    :param filename: полное имя файла-контейнера
    :type filename: string
    :param folder: каталог назначения
    :type folder: string
    :param deflate: паспаковка
    :type deflate: boolean
    :param recursive: рекурсивно достаем все контейнеры
    :type recursive: boolean
    """
    begin = datetime.now()
    print(f'{"Распаковываем бинарник":30}:', end="")
    with open(filename, 'rb') as f:
        ContainerReader(f).extract(folder, deflate, recursive)
    print(f"{datetime.now() - begin}")


def decompress_and_extract(src_folder, dest_folder, *, pool=None):
    helper.clear_dir(dest_folder)
    entries = os.listdir(src_folder)
    tasks = []
    for filename in entries:
        tasks.append([src_folder, filename, dest_folder])

    helper.run_in_pool(decompress_file_and_extract, tasks, pool=pool, title=f'{"Распаковываем контейнеры":30}')


def decompress_file_and_extract(params):
    src_folder, filename, dest_folder = params
    src_path = os.path.join(src_folder, filename)
    dest_path = os.path.join(dest_folder, filename)
    file_is_container = None

    # wbits = -15 т.к. у архивированных файлов нет заголовков
    decompressor = zlib.decompressobj(-15)
    try:
        with open(dest_path, 'wb') as dest:
            with open(src_path, 'rb') as src:
                while True:
                    buf = decompressor.unconsumed_tail
                    if buf == b'':
                        buf = src.read(8192)
                        if buf == b'':
                            break
                    data = decompressor.decompress(buf)
                    if file_is_container is None:
                        file_is_container = data[0:4] == b'\xFF\xFF\xFF\x7F'
                    if data == b'':
                        break
                    dest.write(data)

        # Каждый файл внутри контейнера может быть контейнером
        # Для проверки является ли файл контейнером проверим первые 4 бита
        # Способ проверки ненадежный - нужно придумать что-то другое

        if file_is_container:
            temp_filename = dest_path + ".temp"
            os.rename(dest_path, temp_filename)
            with open(temp_filename, 'rb') as f:
                ContainerReader(f, container=Container).extract(dest_path, recursive=True)
            os.remove(temp_filename)

    except Exception as err:
        raise ExtException(
            parent=err, message="Ошибка при разархифировании контейнера",
            detail=f'{filename} ({err})')
