# -*- coding: utf-8 -*-
import collections
import datetime
import io
import os
import zlib
from struct import pack, unpack, calcsize

from . import helper

# INT32_MAX 7fffffff
END_MARKER = 2147483647
# INT64_MAX ffffffffffffffff для конфигураций старше 8.3.15
END_MARKER_64 = 18446744073709551615
Header = collections.namedtuple('Header', 'first_empty_block_offset, default_block_size')
Block = collections.namedtuple('Block', 'doc_size, current_block_size, next_block_offset, data')
Document = collections.namedtuple('Document', 'size, data')
File = collections.namedtuple('File', 'name, size, created, modified, data')


def read_header(file):
    """
    Считывыет заголовок контейнера.

    :param file: объект файла контейнера
    :type file: BufferedReader
    :return: Заголовок контейнера
    :rtype: Header
    """
    file.seek(0)
    fmt = '4i'
    buff = file.read(calcsize(fmt))
    header = unpack(fmt, buff)
    return Header(header[0] if header[0] != END_MARKER else None, header[1])


def read_block(file, offset, max_data_length=None):
    """
    Считывает блок данных из контейнера.

    :param file: объект файла контейнера
    :type file: BufferedReader
    :param offset: смещение блока в файле контейнера (байт)
    :type offset: int
    :param max_data_length: максимальный размер считываемых данных из блока (байт)
    :type max_data_length: int
    :return: объект блока данных
    :rtype: Block
    """
    file.seek(offset)
    fmt = '2s8s1s8s1s8s1s2s'
    buff = file.read(calcsize(fmt))
    if not buff:
        return
    header = unpack(fmt, buff)

    doc_size = int(header[1], 16)
    current_block_size = int(header[3], 16)
    next_block_offset = int(header[5], 16)

    if max_data_length is None:
        max_data_length = min(current_block_size, doc_size)

    data = file.read(min(current_block_size, max_data_length))

    return Block(doc_size, current_block_size, next_block_offset, data)


def read_document_gen(file, offset):
    """
    Создает генератор чтения данных документа в контейнере.
    Первое значение генератора - размер документа (байт).
    Остальные значения - данные блоков, составляющих документ

    :param file: объект файла контейнера
    :type file: BufferedReader
    :param offset: смещение документа в контейнере (байт)
    :type offset: int
    :return: генератор чтения данных документа
    """
    file.seek(offset)
    header_block = read_block(file, offset)
    if header_block is None:
        return
    else:
        yield header_block.doc_size
        yield header_block.data

        left_bytes = header_block.doc_size - len(header_block.data)
        next_block_offset = header_block.next_block_offset

        while left_bytes > 0 and next_block_offset != END_MARKER:
            block = read_block(file, next_block_offset, left_bytes)
            left_bytes -= len(block.data)
            yield block.data
            next_block_offset = block.next_block_offset


def read_document(file, offset):
    """
    Считывает документ из контейнера. В качестве данных документа возвращается генератор.

    :param file: объект файла контейнера
    :type file: BufferedReader
    :param offset: смещение документа в контейнере
    :type offset: int
    :return: объект документа
    :rtype: Document
    """
    gen = read_document_gen(file, offset)

    try:
        size = next(gen)
    except StopIteration:
        size = 0
    return Document(size, gen)


def read_full_document(file, offset):
    """
    Считывает документ из контейнера. Данные документа считываются целиком.

    :param file: объект файла контейнера
    :type file: BufferedReader
    :param offset: смещение документа в контейнере (байт)
    :type offset: int
    :return: объект документа
    :rtype: Document
    """
    document = read_document(file, offset)
    return Document(document.size, b''.join([chunk for chunk in document.data]))


def parse_datetime(time):
    """
    Преобразует внутренний формат хранения дат файлов в контейнере в обычную дату

    :param time: внутреннее представление даты
    :type time: string
    :return: дата/время
    :rtype: datetime
    """
    # TODO проверить работу на *nix, т.к там начало эпохи - другая дата
    return datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=time * 100)


def read_entries(file):
    """
    Считывает оглавление контейнера

    :param file: объект файла контейнера
    :type file: BufferedReader
    :return: словарь файлов в контейнере
    :rtype: OrderedDict
    """
    # Первый документ после заголовка содержит оглавление
    doc = read_full_document(file, calcsize('4i'))
    table_of_contents = [unpack('2i', x) for x in doc.data.split(pack('i', END_MARKER))[:-1]]

    files = collections.OrderedDict()
    for file_description_offset, file_data_offset in table_of_contents:
        file_description_document = read_full_document(file, file_description_offset)
        file_data = read_document(file, file_data_offset)

        fmt = ''.join(['QQi', str(file_description_document.size - calcsize('QQi')), 's'])
        file_description = unpack(fmt, file_description_document.data)

        # Из описания формата длина имени файла определяется точно, поэтому, теоретически, мусора быть не должно
        # По факту имя часто имеет в конце мусор, который чаще всего состоит из последовательности \x00 n-раз,
        # но иногда бывают и другие символы после \x00. Поэтому применяем вот такой костыль:
        name = file_description[3].decode('utf-16').partition('\x00')[0]
        inner_file = File(name, file_data.size, parse_datetime(file_description[0]),
                          parse_datetime(file_description[1]), file_data.data)

        files[inner_file.name] = inner_file

    return files


class ContainerReader(object):
    """
    Класс для чтения контейнеров
    """

    def __init__(self, file):
        header = read_header(file)
        if header.default_block_size == 0:
            raise BufferError('Container is empty')

        self.file = file
        self.first_empty_block_offset = header.first_empty_block_offset
        self.default_block_size = header.default_block_size
        #: Список файлов в контейнере
        self.entries = read_entries(self.file)

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

    @staticmethod
    def extract_file(filename, file_obj, path, deflate=False, recursive=False):
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
                ContainerReader(f).extract(file_path, recursive=True)
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
    with open(filename, 'rb') as f:
        ContainerReader(f).extract(folder, deflate, recursive)


def decompress_and_extract(src_folder, dest_folder, *, pool=None):
    helper.clear_dir(dest_folder)
    entries = os.listdir(src_folder)

    for filename in entries:
        src_path = os.path.join(src_folder, filename)
        dest_path = os.path.join(dest_folder, filename)
        with open(src_path, 'rb') as f:
            # wbits = -15 т.к. у архивированных файлов нет заголовков
            decompressor = zlib.decompressobj(-15)
            data = decompressor.decompress(f.read())

        # Каждый файл внутри контейнера может быть контейнером
        # Для проверки является ли файл контейнером проверим первые 4 бита
        # Способ проверки ненадежный - нужно придумать что-то другое
        file_is_container = data[0:4] == b'\xFF\xFF\xFF\x7F'

        if file_is_container:
            ContainerReader(io.BytesIO(data)).extract(dest_path, recursive=True)
        else:
            with open(dest_path, 'wb') as f:
                f.write(data)
