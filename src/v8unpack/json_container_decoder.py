import json
import os
import shutil
from base64 import b64decode
from enum import Enum

from . import helper
from .ext_exception import ExtException


class Mode(Enum):
    READ_PARAM = 1
    BEGIN_READ_STRING_VALUE = 2
    BEGIN_READ_MULTI_STRING_VALUE = 6
    END_READ_MULTI_STRING_VALUE = 7
    END_READ_STRING_VALUE = 3
    READ_B64 = 4
    READ_TEXT_FILE = 5


class JsonContainerDecoder:
    def __init__(self, *, src_dir=None, file_name=None):
        self.data = None
        self.raw_data = None
        self.mode = Mode.READ_PARAM
        self.current_object = None
        self.current_value = None
        self.previous_char = None
        self.src_dir = src_dir
        self.file_name = file_name
        self.path = []
        self.params_in_line = 0
        self.line_number = None

    @classmethod
    def decode_mp(cls, params):
        return cls.decode(*params)

    @classmethod
    def decode(cls, params):
        src_dir, file_name, dest_dir = params
        _src_path = os.path.join(src_dir, file_name)
        self = cls(src_dir=src_dir, file_name=file_name)
        encoding = None
        read_as_byte = True
        for code_page in ['utf-8-sig', 'windows-1251']:
            try:
                with open(os.path.join(src_dir, file_name), 'r', encoding=code_page) as entry_file:  # replace BOM
                    try:
                        if entry_file.read(1) == '{':
                            entry_file.seek(0)
                            json.load(entry_file)  # если в файле чистый json воспринимаем его как бинарный файл
                            read_as_byte = True
                        else:
                            read_as_byte = True
                    except json.JSONDecodeError as err:
                        entry_file.seek(0)
                        data = self.decode_file(entry_file)
                        read_as_byte = False
                        encoding = code_page
                        break
            except UnicodeDecodeError:
                continue
            #     try:
            #         with open(os.path.join(src_dir, file_name), 'r', encoding='windows-1251') as entry_file:  # replace BOM
            #             data = self.decode_file(entry_file)
            #             encoding = 'windows-1251'
            #     except UnicodeDecodeError:
            #         read_as_byte = True
            except BigBase64:
                shutil.copy2(os.path.join(src_dir, file_name), os.path.join(dest_dir, file_name + '.c1b64'))
                return
            except Exception as err:
                raise ExtException(parent=err, message=f'Json decode {file_name} error: {err}')
        if read_as_byte:
            shutil.copy2(os.path.join(src_dir, file_name), os.path.join(dest_dir, file_name + '.bin'))
            # with open(os.path.join(src_dir, file_name), 'rb') as entry_file:
            #     data = entry_file.read()
        else:
            if isinstance(data, list):
                with open(f'{os.path.join(dest_dir, file_name)}.json', 'w', encoding='utf-8') as entry_file2:
                    json.dump(data, entry_file2, ensure_ascii=False, indent=2)
            elif isinstance(data, str):
                if encoding is None:
                    encoding = helper.detect_by_bom(_src_path, 'utf-8')
                with open(f'{os.path.join(dest_dir, file_name)}.txt', 'w', encoding=encoding) as entry_file2:
                    entry_file2.write(data)
            # elif isinstance(data, bytes):
            #     with open(f'{os.path.join(dest_dir, file_name)}.bin', 'wb') as entry_file2:
            #         entry_file2.write(data)
            else:
                raise Exception(f'Не поддерживаемый тип данных {type(data)}')

    def decode_file(self, file):
        self.mode = Mode.READ_PARAM
        self.data = []
        self.line_number = 1
        for line in file:
            try:
                self.decode_line(line)
                self.line_number += 1
            except BigBase64 as err:
                raise err from err
            except Exception as err:
                raise ExtException(
                    parent=err,
                    message="Ошибка при разборе скобкофайла",
                    detail=f'{os.path.basename(self.src_dir)}/{self.file_name} проблема до строки {self.line_number}',
                    dump=dict(
                        mode=self.mode,
                        current_object=self.current_object,
                        path=self.path
                    ))
        if self.mode != Mode.READ_PARAM:
            raise ExtException(
                message="Ошибка при разборе скобкофайла",
                detail=f'{os.path.basename(self.src_dir)}/{self.file_name} файл закончен в режиме {self.mode}, '
                       f'создайте проблему на github, укажите текст ошибки и приложите указанный файл'
                # dump=dict(
                #     mode=self.mode,
                #     current_object=self.current_object,
                #     path=self.path
                # )
            )
        if not self.data:
            return ''
        return self.data

    def decode_line(self, line):
        return getattr(self, f'_decode_line_{self.mode.name.lower()}')(line)

    def _decode_line_read_b64(self, line):
        if line == '\n':
            return
        self.decode_b64_line(line, 0)

    def _decode_line_read_text_file(self, line):
        self.data += line

    def _decode_line_read_param(self, line):
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
                # это скорее всего файл целиком из двоичных данных
                if len(self.data) == 1 and len(self.data[0]) == 2 and self.data[0][0] == '1':
                    raise BigBase64()
                self.mode = Mode.READ_B64
                self.decode_b64_line(line, 1)
            else:
                self.decode_object(line[1:])
        elif line[0] == '}':
            self._end_current_object()
            self.decode_object(line[1:])
        elif line[0] == '\n' and self.current_value and len(self.current_value) == 64:
            # self.current_value = self.current_value
            self.mode = Mode.READ_B64
            return
        else:
            if not self.data and self.current_value is None:
                self.data = line
                self.mode = Mode.READ_TEXT_FILE
            elif self.data == [[]] and self.current_value == '':  # текстовый файл с json
                self.data = '{\n' + line
                self.mode = Mode.READ_TEXT_FILE
            else:
                raise ExtException(
                    message='Неожиданное начало объекта',
                    detail=f'в файле :{self.src_dir}/{self.file_name}, path:{self.path})')

    def _decode_line_begin_read_string_value(self, line):
        self.decode_object(line)

    def decode_object(self, line):
        for i, char in enumerate(line):
            if self.mode == Mode.READ_PARAM:
                if char == ',':
                    self._end_value()
                elif char == '}':
                    self._end_current_object()
                elif char == '"':
                    if line.endswith(',"\n') and i == len(line) - 2:
                        self.mode = Mode.BEGIN_READ_MULTI_STRING_VALUE
                        self._add_to_current_value(line[i:])
                        break
                    else:
                        self.mode = Mode.BEGIN_READ_STRING_VALUE
                        self._add_to_current_value(char)
                    pass
                elif char == '\n':
                    break
                else:
                    self._add_to_current_value(char)
            elif self.mode == Mode.BEGIN_READ_STRING_VALUE:
                if char == '"':
                    self.mode = Mode.END_READ_STRING_VALUE
                    self._add_to_current_value(char)
                else:
                    self._add_to_current_value(char)
            elif self.mode == Mode.END_READ_STRING_VALUE:
                if char == '"':
                    self.mode = Mode.BEGIN_READ_STRING_VALUE
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

    def decode_b64_line(self, line, start_pos):
        end_pos = line.find('}')
        if end_pos >= 0:
            self.current_value += line[start_pos:end_pos]
            if start_pos == 1:  # b64 не зарбит на строки
                self.current_value = "#" + self.current_value
            self._end_current_object()
            self.decode_object(line[end_pos + 1:])
            return True
        else:
            self.current_value += line[start_pos:-1]
            return False

    def _decode_line_begin_read_multi_string_value(self, line):
        if line.endswith('",\n'):
            self._add_to_current_value(line[:-2])
            self.mode = Mode.END_READ_MULTI_STRING_VALUE
        else:
            self.current_value += line
            return False

    def _decode_line_end_read_multi_string_value(self, line):
        if line[0] in ['{', '}']:
            self._end_value()
            self._decode_line_read_param(line)
        else:
            self.mode = Mode.BEGIN_READ_MULTI_STRING_VALUE
            self.current_value += ",\n"
            self._decode_line_begin_read_multi_string_value(line)

    def _add_to_current_value(self, value):
        try:
            self.current_value += value
        except TypeError:
            self.current_value = value

    def _end_current_object(self):
        self._end_value()
        if self.path:  # могут быль лишние закрывающие скобки
            self.path.pop()
        self.current_object = self.path[-1] if self.path else None
        self.current_value = None

    def _end_value(self):
        self.mode = Mode.READ_PARAM
        if self.current_value is not None:
            self.current_object.append(self.current_value)
            self.current_value = ''

    @classmethod
    def encode_mp(cls, params):
        return cls.encode(*params)

    @classmethod
    def encode(cls, params):
        src_dir, file_name, dest_dir = params
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
                elif elem.startswith('##base64:'):  # b64 в одну строку
                    raw_data += elem[1:]
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
    helper.run_in_pool(JsonContainerDecoder.decode, tasks, pool=pool, title='Конвертируем скобкофайл в json',
                       need_result=False)


def _decode(src_dir, dest_dir, tasks):
    entries = sorted(os.listdir(src_dir))
    helper.clear_dir(dest_dir)
    for entry in entries:
        src_entry_path = os.path.join(src_dir, entry)
        dest_entry_path = os.path.join(dest_dir, entry)
        if os.path.isdir(src_entry_path):
            try:
                helper.makedirs(dest_entry_path, exist_ok=True)
            except Exception as err:
                raise ExtException(
                    parent=err, message='Ошибка при создании папки',
                    detail=f'{dest_entry_path} ({err})', action='json_decode')
            try:
                _decode(src_entry_path, dest_entry_path, tasks)
            except Exception as err:
                raise ExtException(parent=err, detail=f'{entry} {src_dir}', action='json_decode')
        else:
            tasks.append((src_dir, entry, dest_dir))


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
    helper.run_in_pool(JsonContainerDecoder.encode, tasks, pool=pool, title='Конвертироуем json в скобковайл',
                       need_result=False)


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
                elif extension == 'bin' or extension == 'c1b64':
                    shutil.copy2(
                        os.path.join(src_dir, entry),
                        os.path.join(dest_dir, os.path.splitext(entry)[0])
                    )
                    # with open(src_entry_path, 'rb') as entry_file:
                    #     with open(dest_entry_path[:-3], 'wb') as f:
                    #         f.write(entry_file.read())
                else:
                    tasks.append((src_dir, entry, dest_dir))
        except Exception as err:
            raise ExtException(parent=err, detail=f'{entry} {src_dir}', action='json_encode')


class BigBase64(Exception):
    pass
