# -*- coding: utf-8 -*-
import collections
from datetime import datetime, timedelta
from struct import pack, unpack, calcsize

Header = collections.namedtuple('Header', 'first_empty_block_offset, default_block_size, count_files')
Block = collections.namedtuple('Block', 'doc_size, current_block_size, next_block_offset, data')
Document = collections.namedtuple('Document', 'size, data')
File = collections.namedtuple('File', 'name, size, created, modified, data')


class Container:
    end_marker = 0x7fffffff
    doc_header_fmt = '4i'
    block_header_fmt = '2s8s1s8s1s8s1s2s'
    block_header_fmt_size = 8
    index_fmt = 'i'
    offset_const = 0

    @classmethod
    def read_header(cls, file):
        """
        Считывыет заголовок контейнера.

        :param file: объект файла контейнера
        :type file: BufferedReader
        :return: Заголовок контейнера
        :rtype: Header
        """
        file.seek(0 + cls.offset_const)
        buff = file.read(calcsize(cls.doc_header_fmt))
        header = unpack(cls.doc_header_fmt, buff)
        if header[0] != cls.end_marker:
            raise Exception('Bad container format')
        return Header(header[0], header[1], header[2])

    @classmethod
    def read_block(cls, file, offset, max_data_length=None):
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
        buff = file.read(calcsize(cls.block_header_fmt))
        if not buff:
            return
        header = unpack(cls.block_header_fmt, buff)

        doc_size = int(header[1], 16)
        current_block_size = int(header[3], 16)
        next_block_offset = int(header[5], 16)

        if max_data_length is None:
            max_data_length = min(current_block_size, doc_size)

        data = file.read(min(current_block_size, max_data_length))

        return Block(doc_size, current_block_size, next_block_offset, data)

    @classmethod
    def read_document_gen(cls, file, offset):
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
        header_block = cls.read_block(file, offset)
        if header_block is None:
            return
        else:
            yield header_block.doc_size
            yield header_block.data

            left_bytes = header_block.doc_size - len(header_block.data)
            next_block_offset = header_block.next_block_offset

            while left_bytes > 0 and next_block_offset != cls.end_marker:
                block = cls.read_block(file, next_block_offset, left_bytes)
                left_bytes -= len(block.data)
                yield block.data
                next_block_offset = block.next_block_offset

    @classmethod
    def read_document(cls, file, offset):
        """
        Считывает документ из контейнера. В качестве данных документа возвращается генератор.

        :param file: объект файла контейнера
        :type file: BufferedReader
        :param offset: смещение документа в контейнере
        :type offset: int
        :return: объект документа
        :rtype: Document
        """
        gen = cls.read_document_gen(file, offset)

        try:
            size = next(gen)
        except StopIteration:
            size = 0
        return Document(size, gen)

    @classmethod
    def read_full_document(cls, file, offset):
        """
        Считывает документ из контейнера. Данные документа считываются целиком.

        :param file: объект файла контейнера
        :type file: BufferedReader
        :param offset: смещение документа в контейнере (байт)
        :type offset: int
        :return: объект документа
        :rtype: Document
        """
        document = cls.read_document(file, offset)
        return Document(document.size, b''.join([chunk for chunk in document.data]))

    @classmethod
    def parse_datetime(cls, time):
        """
        Преобразует внутренний формат хранения дат файлов в контейнере в обычную дату

        :param time: внутреннее представление даты
        :type time: string
        :return: дата/время
        :rtype: datetime
        """
        # TODO проверить работу на *nix, т.к там начало эпохи - другая дата
        return datetime(1, 1, 1) + timedelta(microseconds=(time * 100))

    @classmethod
    def read_entries(cls, file):
        """
        Считывает оглавление контейнера

        :param file: объект файла контейнера
        :type file: BufferedReader
        :return: словарь файлов в контейнере
        :rtype: OrderedDict
        """
        # Первый документ после заголовка содержит оглавление
        doc = cls.read_full_document(file, calcsize(cls.doc_header_fmt) + cls.offset_const)
        table_of_contents = [unpack(f'2{cls.index_fmt}', x) for x in
                             doc.data.split(pack(cls.index_fmt, cls.end_marker))[:-1]]

        files = collections.OrderedDict()
        for file_description_offset, file_data_offset in table_of_contents:
            file_description_document = cls.read_full_document(file, file_description_offset + cls.offset_const)
            file_data = cls.read_document(file, file_data_offset + cls.offset_const)

            fmt = ''.join(['QQi', str(file_description_document.size - calcsize('QQi')), 's'])
            file_description = unpack(fmt, file_description_document.data)

            # Из описания формата длина имени файла определяется точно, поэтому, теоретически, мусора быть не должно
            # По факту имя часто имеет в конце мусор, который чаще всего состоит из последовательности \x00 n-раз,
            # но иногда бывают и другие символы после \x00. Поэтому применяем вот такой костыль:
            name = file_description[3].decode('utf-16').partition('\x00')[0]
            inner_file = File(name, file_data.size, cls.parse_datetime(file_description[0]),
                              cls.parse_datetime(file_description[1]), file_data.data)

            files[inner_file.name] = inner_file

        return files


class Container64(Container):
    end_marker = 0xffffffffffffffff  # 18446744073709551615
    doc_header_fmt = '1Q3i'
    block_header_fmt = '2s16s1s16s1s16s1s2s'
    block_header_fmt_size = 16
    index_fmt = 'Q'
    offset_const = 0x1359
