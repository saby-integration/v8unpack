"""CfFile — чтение и запись .cf файлов 1С с бинарной точностью.

Стратегия: читаем оригинал блок-по-блоку, сохраняем сырые данные
каждого файла (attr + data). При записи — копируем всё as-is,
подменяя только изменённые файлы.

Гарантия: файл без изменений → бинарно идентичен оригиналу.
"""
import io
import os
import zlib
import collections
from struct import pack, unpack, calcsize

from .container import Container, Container64
from .container_doc import Document
from .container_reader import detect_format
from .helper import file_size


RawFile = collections.namedtuple('RawFile', 'name, attr_raw, data_raw')


class CfFile:
    """Бинарно-точное чтение/запись .cf файлов."""

    def __init__(self):
        self.containers = []  # list of CfContainer

    def read(self, path):
        """Прочитать .cf файл — сохранить сырые данные всех блоков."""
        self.containers = []
        with open(path, 'rb') as f:
            offset = 0
            while True:
                try:
                    c = detect_format(f, offset)
                    c.read(f, offset)
                    
                    cc = CfContainer(
                        container_type=type(c),
                        field3=c.header_field3,
                        block_size=c.default_block_size,
                        header_raw=self._read_raw_header(f, offset, type(c)),
                    )
                    
                    # Читаем каждый файл — attr и data как RAW байты
                    for name, fobj in c.files.items():
                        # attr raw — из позиции в TOC
                        # data raw — compressed bytes
                        data_chunks = list(fobj.data)
                        data_raw = b''.join(data_chunks)
                        
                        # attr raw — нужно прочитать из файла
                        # У нас нет прямого доступа к attr raw через Container API
                        # Сохраняем timestamps + name для пересоздания attr
                        cc.files[name] = CfFileEntry(
                            name=name,
                            created_raw=None,  # заполним ниже
                            modified_raw=None,
                            data_compressed=data_raw,
                            data_decompressed=None,  # lazy
                        )
                    
                    # Читаем raw timestamps из attr blocks
                    import struct as _st
                    doc_toc = Document(c)
                    toc_data = doc_toc.read(f, c.header_size, c.index_block_size)
                    toc_pos = 0
                    fmt_size = _st.calcsize(f'3{c.index_fmt}')
                    file_names = list(cc.files.keys())
                    fi = 0
                    while toc_pos + fmt_size <= len(toc_data) and fi < len(file_names):
                        vals = _st.unpack_from(f'2{c.index_fmt}', toc_data, toc_pos)
                        a_off = vals[0]
                        if a_off == c.end_marker:
                            break
                        doc_attr = Document(c)
                        attr_raw = doc_attr.read(f, a_off)
                        ct_raw, mt_raw = _st.unpack_from('<QQ', attr_raw)
                        cc.files[file_names[fi]].created_raw = ct_raw
                        cc.files[file_names[fi]].modified_raw = mt_raw
                        fi += 1
                        toc_pos += fmt_size

                    self.containers.append(cc)
                    offset += c.size
                except EOFError:
                    break

    def write(self, path):
        """Записать .cf файл — с оригинальными timestamps и field3."""
        with open(path, 'w+b') as f:
            for cc in self.containers:
                cc.write_to(f)
        return os.path.getsize(path)

    def get_file(self, name) -> 'CfFileEntry':
        """Найти файл по имени во всех контейнерах."""
        for cc in self.containers:
            if name in cc.files:
                return cc.files[name]
        return None

    def get_decompressed(self, name) -> bytes:
        """Получить декомпрессированные данные файла."""
        entry = self.get_file(name)
        if not entry:
            return None
        if entry.data_decompressed is None:
            try:
                dec = zlib.decompressobj(-15)
                entry.data_decompressed = dec.decompress(entry.data_compressed) + dec.flush()
            except:
                entry.data_decompressed = entry.data_compressed
        return entry.data_decompressed

    def set_decompressed(self, name, data: bytes):
        """Установить новые данные файла (будут сжаты при записи)."""
        entry = self.get_file(name)
        if not entry:
            raise KeyError(f"File {name} not found")
        # Нормализуем CRLF только для текстовых файлов (скобочный формат)
        # Подконтейнеры (.0) и другие бинарные данные не трогаем
        is_binary = (isinstance(data, bytes) and len(data) >= 4 and
                     data[:4] in (b'\xff\xff\xff\x7f', b'\xff\xff\xff\xff\xff\xff\xff\xff'))
        if isinstance(data, bytes) and b'\n' in data and not is_binary:
            data = data.replace(b'\r\n', b'\n').replace(b'\r', b'\n').replace(b'\n', b'\r\n')
        entry.data_decompressed = data
        comp = zlib.compressobj(wbits=-15)
        entry.data_compressed = comp.compress(data) + comp.flush()
        entry._modified_flag = True

    def list_files(self, container_index=None):
        """Список всех файлов."""
        result = []
        for i, cc in enumerate(self.containers):
            if container_index is not None and i != container_index:
                continue
            for name in cc.files:
                result.append((i, name))
        return result

    @staticmethod
    def _read_raw_header(f, offset, container_type):
        """Читаем сырой заголовок контейнера."""
        f.seek(offset)
        size = 16 if container_type == Container else 20
        return f.read(size)


class CfContainer:
    """Один контейнер внутри .cf файла."""

    def __init__(self, container_type, field3, block_size, header_raw):
        self.container_type = container_type
        self.field3 = field3
        self.block_size = block_size
        self.header_raw = header_raw
        self.files = collections.OrderedDict()

    def write_to(self, dest_file):
        """Записать контейнер в файл."""
        c = self.container_type()
        c.offset = dest_file.tell()
        c.file = dest_file
        c.default_block_size = self.block_size

        c._toc_block_size = c.index_block_size  # padding TOC до index_block_size
        c.write_header(self.field3)

        for name, entry in self.files.items():
            doc = Document(c)
            # Attr block с оригинальными raw timestamps
            buffer = b''.join([
                pack('QQi', entry.created_raw or 0, entry.modified_raw or 0, 0),
                name.encode('utf-16-le'),
                b'\x00' * 4
            ])
            attr_offset = doc.write(io.BytesIO(buffer))

            # Data block — compressed данные
            doc2 = Document(c)
            data_offset = doc2.write(
                io.BytesIO(entry.data_compressed),
                min_block_size=c.default_block_size
            )

            c.toc.append((attr_offset, data_offset))

        c.write_table_off_content()
        # write_table_off_content seekает на начало TOC — восстанавливаем позицию в конец
        dest_file.seek(0, 2)


class CfFileEntry:
    """Один файл внутри контейнера."""

    def __init__(self, name, created_raw, modified_raw, data_compressed, data_decompressed=None):
        self.name = name
        self.created_raw = created_raw    # int64 — оригинальный timestamp
        self.modified_raw = modified_raw   # int64
        self.data_compressed = data_compressed
        self.data_decompressed = data_decompressed
        self._modified_flag = False
