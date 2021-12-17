import json
import os
from base64 import b64decode

from . import helper
from .ext_exception import ExtException

READ_PARAM = 1
BEGIN_READ_STRING_VALUE = 2
END_READ_STRING_VALUE = 3
READ_B64 = 4
READ_TEXT_FILE = 5


class JsonContainerDecoder:
    def __init__(self, *, src_dir=None, file_name=None):
        self.data = None
        self.raw_data = None
        self.mode = READ_PARAM
        self.current_object = None
        self.current_value = None
        self.previous_char = None
        self.src_dir = src_dir
        self.file_name = file_name
        self.path = []
        self.params_in_line = 0

    @classmethod
    def decode_mp(cls, params):
        return cls.decode(*params)

    @classmethod
    def decode(cls, src_dir, file_name, dest_dir=None):
        _src_path = os.path.join(src_dir, file_name)
        self = cls(src_dir=src_dir, file_name=file_name)
        encoding = None
        try:
            with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8-sig') as entry_file:  # replace BOM
                data = self.decode_file(entry_file)
        except UnicodeDecodeError:
            try:
                with open(os.path.join(src_dir, file_name), 'r', encoding='windows-1251') as entry_file:  # replace BOM
                    data = self.decode_file(entry_file)
                    encoding = 'windows-1251'
            except UnicodeDecodeError:
                with open(os.path.join(src_dir, file_name), 'rb') as entry_file:
                    data = entry_file.read()
        except Exception as err:
            raise ExtException(parent=err, message=f'Json decode {file_name} error: {err}')

        if dest_dir is not None:
            if isinstance(data, list):
                with open(f'{os.path.join(dest_dir, file_name)}.json', 'w', encoding='utf-8') as entry_file2:
                    json.dump(data, entry_file2, ensure_ascii=False, indent=2)
            elif isinstance(data, str):
                if encoding is None:
                    encoding = helper.detect_by_bom(_src_path, 'utf-8')
                with open(f'{os.path.join(dest_dir, file_name)}.txt', 'w', encoding=encoding) as entry_file2:
                    entry_file2.write(data)
            elif isinstance(data, bytes):
                with open(f'{os.path.join(dest_dir, file_name)}.bin', 'wb') as entry_file2:
                    entry_file2.write(data)
            else:
                raise Exception(f'Не поддерживаемый тип данных {type(data)}')
        return data

    def decode_file(self, file):
        self.mode = READ_PARAM
        self.data = []
        for line in file:
            self.decode_line(line)
        if not self.data:
            return ''
        return self.data

    def decode_line(self, line):
        if self.mode == READ_PARAM:
            if line[0] == '{':  # новый объект, исходим из того, что формат записи предполагает только один новый объект
                if self.current_object is None:
                    self.current_object = []
                    self.data.append(self.current_object)
                    self.path.append(self.current_object)
                else:
                    self.current_object.append([])
                    self.current_object = self.current_object[-1]
                    self.path.append(self.current_object)

                self.current_value = ''
                if line.startswith('{#base64'):
                    self.mode = READ_B64
                    self.current_value += line[1:-1]
                else:
                    self.decode_object(line[1:])
            elif line[0] == '}':
                self._end_current_object()
                self.decode_object(line[1:])
            elif line[0] == '\n' and self.current_value and len(self.current_value) == 64:
                # self.current_value = self.current_value
                self.mode = READ_B64
                return
            else:
                if not self.data and self.current_value is None:
                    self.data = line
                    self.mode = READ_TEXT_FILE
                else:
                    raise Exception(
                        f'неожиданное начало объекта file:{self.src_dir}/{self.file_name}, path:{self.path})')
        elif self.mode == BEGIN_READ_STRING_VALUE:
            if line.endswith('",\n') and not line.endswith('"",\n'):
                self.current_value += line[:-2]
                self._end_value()
            else:
                self.current_value += line
        elif self.mode == READ_B64:
            if line == '\n':
                return
            end_pos = line.find('}')
            if end_pos >= 0:
                self.current_value += line[:end_pos]
                self._end_current_object()
                self.decode_object(line[end_pos + 1:])
            else:
                self.current_value += line[:-1]
        elif self.mode == READ_TEXT_FILE:
            self.data += line
        else:
            raise NotImplemented(f'mode {self.mode}')

    def decode_object(self, line):
        for char in line:
            if self.mode == READ_PARAM:
                if char == ',':
                    self._end_value()
                elif char == '}':
                    self._end_current_object()
                elif char == '"':
                    self.mode = BEGIN_READ_STRING_VALUE
                    self._add_to_current_value(char)
                    pass
                elif char == '\n':
                    break
                else:
                    self._add_to_current_value(char)
            elif self.mode == BEGIN_READ_STRING_VALUE:
                if char == '"':
                    self.mode = END_READ_STRING_VALUE
                    self._add_to_current_value(char)
                else:
                    self._add_to_current_value(char)
            elif self.mode == END_READ_STRING_VALUE:
                if char == '"':
                    self.mode = BEGIN_READ_STRING_VALUE
                    self._add_to_current_value(char)
                elif char == ',':
                    self._end_value()
                elif char == '}':
                    self._end_current_object()
                else:
                    self._add_to_current_value(char)
            else:
                raise NotImplemented(f'mode {self.mode}')
        # if self.current_value:
        #     self.current_object.append(self.current_value)
        #     self.current_value = ''

    def _add_to_current_value(self, value):
        try:
            self.current_value += value
        except TypeError:
            self.current_value = value

    def _end_current_object(self):
        self.mode = READ_PARAM
        self._end_value()
        self.path.pop()
        self.current_object = self.path[-1] if self.path else None
        self.current_value = None

    def _end_value(self):
        self.mode = READ_PARAM
        if self.current_value is not None:
            self.current_object.append(self.current_value)
            self.current_value = ''

    @classmethod
    def encode_mp(cls, params):
        return cls.encode(*params)

    @classmethod
    def encode(cls, src_dir, file_name, dest_dir=None):
        try:
            # try:
            with open(os.path.join(src_dir, file_name), 'r', encoding='utf-8') as file:
                data = json.load(file)
            self = cls(src_dir=src_dir, file_name=file_name)
            raw_data = self.encode_root_object(data)
            if dest_dir is not None:
                cls.write_data(dest_dir, file_name[:-5], raw_data)
            return raw_data
        except Exception as err:
            raise ExtException(parent=err, detail=file_name) from err

    def encode_root_object(self, data):
        raw_data = ''
        for elem in data:
            if raw_data:
                raw_data += ',\n'
            raw_data += self.encode_object(elem, True)
        return raw_data

    def encode_object(self, data, first=True):
        if first:
            raw_data = '{'
        else:
            raw_data = '\n{'
            self.params_in_line = 0
        data_len = len(data)
        for i in range(data_len):
            elem = data[i]
            if isinstance(elem, list):
                raw_data += self.encode_object(elem, False)
                if i == data_len - 1:
                    raw_data += '\n'
                    self.params_in_line = 0
                pass
            elif isinstance(elem, str):
                if elem.startswith('#base64:'):
                    j = 72
                    raw_data += f'{elem[0:j]}'
                    while j <= len(elem):
                        raw_data += f'\r\n{elem[j: j + 64]}'
                        j += 64
                else:
                    j = len(elem)
                    is_base64 = False
                    if j > 64:  # base64 нужно переносить
                        try:
                            b64decode(elem)
                            is_base64 = True
                        except ValueError:
                            pass

                    if is_base64:
                        _first = True
                        while j:
                            if _first:
                                _first = False
                            else:
                                raw_data += '\r\n'

                            if j > 64:
                                raw_data += elem[:64]
                                elem = elem[64:]
                                j = len(elem)
                            else:
                                raw_data += elem
                                break
                    else:
                        raw_data += elem

            if i != data_len - 1:
                raw_data += ','
                self.params_in_line += 1

        raw_data += '}'
        return raw_data
        pass

    @staticmethod
    def write_data(dest_dir, file_name, data):
        with open(os.path.join(dest_dir, file_name), 'w', encoding='utf-8-sig') as f:  # replace BOM
            return f.write(data)


def json_decode(src_dir, dest_dir, *, pool=None):
    """
    Рекурсивно добавляет файлы из директории в контейнер

    :param src_dir: каталог файлов, результатов работы v8unpack -U
    :type src_dir: string
    :param dest_dir: каталог файлов, в который будут помещены json файлы
    :type dest_dir: string
    :param pool: пул процессов для параллельного выполнения, если не передан будет поднят свой
    :type: pool: Multiprocessing Pool
    """
    tasks = []
    _decode(src_dir, dest_dir, tasks)
    helper.run_in_pool(JsonContainerDecoder.decode, tasks, pool=pool)


def _decode(src_dir, dest_dir, tasks):
    entries = sorted(os.listdir(src_dir))
    helper.clear_dir(dest_dir)
    for entry in entries:
        try:
            src_entry_path = os.path.join(src_dir, entry)
            dest_entry_path = os.path.join(dest_dir, entry)
            if os.path.isdir(src_entry_path):
                os.mkdir(dest_entry_path)
                _decode(src_entry_path, dest_entry_path, tasks)
            else:
                tasks.append((src_dir, entry, dest_dir))
        except Exception as err:
            raise ExtException(parent=err, detail=f'{entry} {src_dir}', action='json_decode')


def json_encode(src_dir, dest_dir, *, pool=None):
    """
    Распаковка контейнера. Сахар для ContainerReader

    :param src_dir: каталог файлов, результатов работы v8unpack -U
    :type src_dir: string
    :param dest_dir: каталог файлов, в который будут помещены json файлы
    :type dest_dir: string
    :param pool: пул процессов для параллельного выполнения, если не передан будет поднят свой
    :type: pool: Multiprocessing Pool
    """
    tasks = []
    helper.clear_dir(dest_dir)
    _encode(src_dir, dest_dir, tasks)
    helper.run_in_pool(JsonContainerDecoder.encode, tasks, pool=pool)


def _encode(src_dir, dest_dir, tasks):
    entries = os.listdir(src_dir)
    for entry in entries:
        try:
            src_entry_path = os.path.join(src_dir, entry)
            dest_entry_path = os.path.join(dest_dir, entry)
            if os.path.isdir(src_entry_path):
                os.mkdir(dest_entry_path)
                _encode(src_entry_path, dest_entry_path, tasks)
            else:
                extension = entry.split('.')[-1]
                if extension == 'txt':
                    encoding = helper.detect_by_bom(src_entry_path, 'utf-8')
                    try:
                        with open(src_entry_path, 'r', encoding=encoding) as entry_file:
                            with open(dest_entry_path[:-3], 'w', encoding=encoding) as f:
                                f.write(entry_file.read())
                    except UnicodeDecodeError:
                        encoding = 'windows-1251'
                        with open(src_entry_path, 'r', encoding=encoding) as entry_file:
                            with open(dest_entry_path[:-3], 'w', encoding=encoding) as f:
                                f.write(entry_file.read())
                elif extension == 'bin':
                    with open(src_entry_path, 'rb') as entry_file:
                        with open(dest_entry_path[:-3], 'wb') as f:
                            f.write(entry_file.read())
                else:
                    tasks.append((src_dir, entry, dest_dir))
        except Exception as err:
            raise ExtException(parent=err, detail=f'{entry} {src_dir}', action='json_encode')
