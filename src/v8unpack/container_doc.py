# -*- coding: utf-8 -*-
import collections
import datetime
import io
import os
import tempfile
import zlib
from datetime import datetime, timedelta
from struct import pack, calcsize
# -*- coding: utf-8 -*-
from struct import unpack

from .helper import file_size

Header = collections.namedtuple('Header', 'first_empty_block_offset, default_block_size, count_files')
Block = collections.namedtuple('Block', 'doc_size, current_block_size, next_block_offset, data')
File = collections.namedtuple('File', 'name, size, created, modified, data')
DocumentData = collections.namedtuple('DocumentData', 'size, data')

# Размер буффера передачи данных из потока в поток
BUFFER_CHUNK_SIZE = 512


class Document:
    def __init__(self, container):
        self.container = container
        self.full_size = 0  # include all header size
        self.data_size = 0

    def read(self, file, offset):
        document_data = self.read_chunk(file, offset)
        return b''.join([chunk for chunk in document_data])

    def read_chunk(self, file, offset):
        """
        Считывает документ из контейнера. В качестве данных документа возвращается генератор.

        :param file: объект файла контейнера
        :type file: BufferedReader
        :param offset: смещение документа в контейнере
        :type offset: int
        :return: данные документа
        :rtype:
        """
        gen = self._read_gen(file, offset)

        try:
            self.data_size = next(gen)
        except StopIteration:
            self.data_size = 0

        return gen

    def _read_gen(self, file, offset):
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
        header_block = self.read_block(file, offset)
        if header_block is None:
            return
        else:
            yield header_block.doc_size
            yield header_block.data

            left_bytes = header_block.doc_size - len(header_block.data)
            next_block_offset = header_block.next_block_offset

            while left_bytes > 0 and next_block_offset != self.container.end_marker:
                block = self.read_block(file, next_block_offset, left_bytes)
                left_bytes -= len(block.data)
                yield block.data
                next_block_offset = block.next_block_offset

    def read_block(self, file, offset, max_data_length=None):
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
        file.seek(offset + self.container.offset)
        header_size = self.container.block_header_size
        buff = file.read(header_size)
        if not buff:
            return
        header = unpack(self.container.block_header_fmt, buff)

        doc_size = int(header[1], 16)
        current_block_size = int(header[3], 16)
        next_block_offset = int(header[5], 16)

        if max_data_length is None:
            max_data_length = min(current_block_size, doc_size)

        data_size = min(current_block_size, max_data_length)

        data = file.read(data_size)
        self.full_size += header_size + current_block_size

        return Block(doc_size, current_block_size, next_block_offset, data)

    def write_header(self, file, file_name):
        modify_time = epoch2int(os.stat(file.fileno()).st_mtime)
        # В *nix это не время создания файла.
        creation_time = epoch2int(os.stat(file.fileno()).st_ctime)
        buffer = b''.join([pack('QQi', creation_time, modify_time, 0), file_name.encode('utf-16-le'), b'\x00' * 4])
        attribute_doc_offset = self.write(io.BytesIO(buffer))
        return attribute_doc_offset

    def write(self, data, *, min_block_size=0):
        return self.write_block(data, doc_size=file_size(data), min_block_size=min_block_size)

    def write_block(self, data, *, doc_size=0, min_block_size=0, offset=None, next_block_offset=None):
        """
        Записывает блок данных в контейнер

        :param data: file-like объект
        :param kwargs: Опциональные параметры
        :return: смещение записанных данных (байт)
        :rtype: int
        """
        if offset is not None:
            self.container.file.seek(offset)
        else:
            offset = file_size(self.container.file)
        block_size = file_size(data)
        min_block_size = max(min_block_size, block_size)
        if not next_block_offset:
            next_block_offset = self.container.end_marker

        header_data = ('\r\n', self.container.int2hex(doc_size), ' ', self.container.int2hex(min_block_size), ' ',
                       self.container.int2hex(next_block_offset), ' ', '\r\n')
        header = pack(self.container.block_header_fmt, *[x.encode() for x in header_data])

        self.container.file.write(header)
        self.write_block_data(data, self.container.file)

        self.container.file.write(b'\x00' * (min_block_size - data.tell()))

        return offset

    def compress(self, src_fd):
        with tempfile.TemporaryFile() as f:
            compressor = zlib.compressobj(wbits=-15)
            src_fd.seek(0)
            while True:
                chunk = src_fd.read(BUFFER_CHUNK_SIZE)
                if not chunk:
                    f.write(compressor.flush())
                    break
                f.write(compressor.compress(chunk))
            data_doc_offset = self.write(f)
        return data_doc_offset

    @staticmethod
    def write_block_data(data, dest_file):
        data.seek(0)
        while True:
            buffer = data.read(BUFFER_CHUNK_SIZE)
            if not buffer:
                break
            dest_file.write(buffer)


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
    return (datetime.fromtimestamp(epoch_time) - datetime(1, 1, 1)) // timedelta(
        microseconds=100)

