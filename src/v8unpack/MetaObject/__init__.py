import os
import re
import shutil
from base64 import b64decode, b64encode
from uuid import uuid4

from .. import helper
from ..ext_exception import ExtException
from ..metadata_types import MetaDataTypes


class MetaObject:
    ext_code = {'obj': 0}
    encrypted_types = ['text', 'image', 'bin']
    _unknown_binary = None
    _obj_info = None
    _obj_name = None

    re_meta_data_obj = re.compile('^[^.]+\.json$')
    directive_1c_uncomment = re.compile('(?P<n>\\n)(?P<d>#Область|#КонецОбласти|&НаСервере|&НаКлиенте)')
    directive_1c_comment = re.compile('(?P<n>\\n)(?P<c>// v8unpack )(?P<d>[#|&])')

    def __init__(self, *, meta_obj_class=None, obj_version='803', options=None):
        self.meta_obj_class = meta_obj_class
        self.header = {}
        self.uuid = None
        self.name = None
        self.code = {}
        self.file_list = []
        self.obj_version = obj_version
        self.options = options

    def get_options(self, name, default=None):
        try:
            return self.options[name]
        except (TypeError, KeyError):
            return default

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][1]

    def decode_header(self, header_data, *, id_in_separate_file=True):
        try:
            header = self.get_decode_header(header_data)
            helper.decode_header(self.header, header, id_in_separate_file=id_in_separate_file)
            self.uuid = self.header['uuid']
            self.name = self.header['name']
            self.header['header'] = header_data
        except Exception as err:
            raise ExtException(parent=err)

    def encode_header(self):
        header = self.get_decode_header(self.header['header'])
        helper.encode_header(self.header, header)

    def decode_includes(self, src_dir, dest_dir, dest_path, header_data):
        tasks = []
        includes = self.get_decode_includes(header_data)
        for include in includes:
            self.decode_include(src_dir, dest_dir, dest_path, tasks, include)
        return tasks

    def decode_include(self, src_dir, dest_dir, dest_path, tasks, include):
        auto_include = self.get_options('auto_include')
        try:
            count_include_types = int(include[2])
        except IndexError:
            raise ExtException(message='Include types not found', detail=self.__class__.__name__)
        for i in range(count_include_types):
            _metadata = include[i + 3]
            _count_obj = int(_metadata[1])
            _metadata_type_uuid = _metadata[0]
            try:
                metadata_type = MetaDataTypes(_metadata_type_uuid)
            except ValueError:
                # data = helper.json_read(src_dir, f'{_metadata[2]}.json')  # чтобы посмотреть что это
                # continue

                if not _count_obj:
                    continue

                if not isinstance(_metadata[2], str):  # вложенный объект
                    continue
                msg = f'У {self.__class__.__name__} {self.header["name"]} неизвестный тип вложенных метаданных: {_metadata_type_uuid} лежит в файле {_metadata[2]}'
                print(msg)
                continue
                # raise Exception(msg)
            if not _count_obj:
                continue
            new_dest_path = os.path.join(dest_path, metadata_type.name)
            external_obj = False
            internal_obj = False
            for j in range(_count_obj):
                obj_data = _metadata[j + 2]
                if isinstance(obj_data, str):
                    if j == 0:
                        os.mkdir(os.path.join(dest_dir, new_dest_path))

                    tasks.append([metadata_type.name, [src_dir, obj_data, dest_dir, new_dest_path, self.options]])
                    external_obj = True
                elif isinstance(obj_data, list):
                    if not metadata_type:
                        continue
                    try:
                        handler = helper.get_class_metadata_object(metadata_type.name)
                    except Exception as err:
                        continue
                    if j == 0:
                        os.mkdir(os.path.join(dest_dir, new_dest_path))
                    obj_uuid = handler.decode_internal_include(self, obj_data, src_dir, dest_dir, new_dest_path,
                                                               self.options)
                    if not auto_include:
                        # заменяем данные на идентификатор
                        _metadata[j + 2] = obj_uuid
                    internal_obj = True
            if (external_obj or internal_obj) and auto_include:  # todo dynamic index
                include[i + 3] = metadata_type.name

    @classmethod
    def get_decode_includes(cls, header_data: list) -> list:
        raise NotImplementedError(f'Для метаданных {cls.__name__} не указана ссылка на includes')

    def fill_header_includes(self, include_index):
        try:
            includes = self.get_decode_includes(self.header['header'])
        except NotImplementedError:
            return
        for include in includes:
            try:
                count_include_types = int(include[2])
            except IndexError:
                raise ExtException(message='Include types not found', detail=self.__class__.__name__)
            try:
                for i in range(count_include_types):
                    self.fill_header_include(i, include, include_index)
            except Exception as err:
                raise ExtException(parent=err)

    def fill_header_include(self, i, include, include_index):
        _metadata = include[i + 3]
        if isinstance(_metadata, str):  # лежит идентификатор типа режим auto_include
            metadata_type = MetaDataTypes[_metadata]
            internal_data = include_index.get(_metadata, [])

            include_objects = sorted(internal_data, key=lambda d: d[1])
            include_objects = list(map(lambda d: d[2], include_objects))

            include[i + 3] = [metadata_type.value, str(len(include_objects)), *include_objects]

            internal_data = include_index.get(metadata_type)
            if not internal_data:
                return

        elif isinstance(_metadata, list):  # лежат типы как положено
            _count_obj = int(_metadata[1])
            _metadata_type_uuid = _metadata[0]
            try:
                metadata_type = MetaDataTypes(_metadata_type_uuid)
            except ValueError:
                return
            internal_data = include_index.get(metadata_type.name)
            if not internal_data:
                return
            # данные простых объектов пришли из внешних файлов и нужно поместить из в объект
            internal_data_uuid = {}
            for i, elem in enumerate(internal_data):
                internal_data_uuid[elem[0].lower()] = i
            for j in range(_count_obj):
                obj_uuid = _metadata[j + 2]
                if not isinstance(obj_uuid, str):
                    raise NotImplementedError('Плохой файл, должны быть просто идентификаторы')
                try:
                    index = internal_data_uuid[obj_uuid.lower()]
                except KeyError:
                    raise ExtException(message='Не найдены данные внутреннего типа',
                                       detail=f"{metadata_type.name} {obj_uuid}")
                _metadata[j + 2] = internal_data[index][2]

    def encode_includes(self, src_dir, file_name, dest_dir, parent_id):
        tasks = []
        includes = []
        entries = sorted(os.listdir(src_dir))
        for entry in entries:
            src_entry_path = os.path.join(src_dir, entry)
            if os.path.isdir(src_entry_path):
                try:
                    MetaDataTypes[entry]
                except KeyError:
                    raise Exception(
                        f'Обнаружен не поддерживаемый тип метаданных или некорректно описанная область {entry} ')

                handler = helper.get_class_metadata_object(entry)
                _src_dir = os.path.join(src_dir, entry)
                handler.encode_get_include_obj(_src_dir, dest_dir, handler.__name__, tasks,
                                               self.options, parent_id, {})
        return tasks

    @classmethod
    def encode_get_include_obj(cls, src_dir, dest_dir, include, tasks, options, parent_id, include_index):
        entries = os.listdir(src_dir)
        for entry in entries:
            if os.path.isdir(os.path.join(src_dir, entry)):
                new_src_dir = os.path.join(src_dir, entry)
                tasks.append([include, [new_src_dir, entry, dest_dir, options, parent_id, include_index]])
        # cls.encode_get_include_obj_from_named_folder(src_dir, dest_dir, include, tasks, options, parent_id,
        #                                              include_index)

    # @classmethod
    # def encode_get_include_obj(cls, src_dir, dest_dir, include, tasks, options, parent_id, include_index):
    #     """
    #     возвращает список задач на парсинг объектов этого типа
    #     """
    #     entries = os.listdir(src_dir)
    #     for entry in entries:
    #         if cls.re_meta_data_obj.fullmatch(entry):
    #             tasks.append([include, [src_dir, entry[:-5], dest_dir, options, parent_id, include_index]])

    @classmethod
    def encode_versions(cls, file_list):
        versions = ["1", str(len(file_list) + 1), helper.str_encode(""), str(uuid4())]
        for file_name in file_list:
            versions.append(helper.str_encode(file_name))
            versions.append(str(uuid4()))
        return [versions]

    # @classmethod
    # def encode_get_include_obj_from_named_folder(cls, src_dir, dest_dir, include, tasks, options, parent_id,
    #                                              include_index):
    #     """
    #     возвращает список задач на парсинг объектов этого типа
    #     """
    #     entries = os.listdir(src_dir)
    #     for entry in entries:
    #         if os.path.isdir(os.path.join(src_dir, entry)):
    #             new_src_dir = os.path.join(src_dir, entry)
    #             tasks.append([include, [new_src_dir, entry, dest_dir, options, parent_id, include_index]])

    def encode_version(self):
        return self.data['file_version']

    def get_class_name_without_version(self):
        return self.__class__.__name__
        # _version = version if version else cls.version
        # if _version and cls.__name__.endswith(_version):
        #     return cls.__name__[:len(_version) * -1]
        # return cls.__name__

    def read_raw_code(self, src_dir, file_name, *, uncomment_directive=False):
        encoding = 'utf-8'
        try:
            code = helper.txt_read(src_dir, file_name, encoding=encoding)
            encoding = helper.detect_by_bom(os.path.join(src_dir, file_name), 'utf-8')
        except FileNotFoundError as err:
            code = None
        except UnicodeDecodeError:
            try:
                encoding = 'windows-1251'
                code = helper.txt_read(src_dir, file_name, encoding=encoding)
            except UnicodeDecodeError:
                encoding = 'bin'
                code = helper.bin_read(src_dir, file_name)

        if code and encoding != 'bin':
            # if self.options['version'] in ['801', '802'] or uncomment_directive:  # раскомментируем директивы
            if uncomment_directive:  # раскомментируем директивы
                code = self.directive_1c_comment.sub(r'\g<n>\g<d>', code)
        return code, encoding

    def write_raw_code(self, code, dest_dir, filename, *, encoding='uft-8', comment_directive=False):
        if code is not None:
            # if self.options['version'] in ['801', '802'] or comment_directive:  # комментируем директивы
            if comment_directive:  # комментируем директивы
                code = self.directive_1c_uncomment.sub(r'\g<n>// v8unpack \g<d>', code)
            helper.txt_write(code, dest_dir, filename, encoding=encoding)

    def decode_code(self, src_dir, *, uncomment_directive=False):
        for code_name in self.ext_code:
            if code_name in self.code:
                continue  # код был в файле с формой
            _obj_code_dir = f'{os.path.join(src_dir, self.header["uuid"])}.{self.ext_code[code_name]}'
            if not os.path.exists(_obj_code_dir):
                continue
            if os.path.isdir(_obj_code_dir):
                self.header[f'code_info_{code_name}'] = helper.brace_file_read(_obj_code_dir, 'info')
                try:
                    self.code[code_name], encoding = self.read_raw_code(_obj_code_dir, 'text',
                                                                        uncomment_directive=uncomment_directive)
                    self.header[f'code_encoding_{code_name}'] = encoding  # можно безболезненно поменять на utf-8-sig
                except FileNotFoundError as err:
                    # todo могут быть зашифрованные модули тогда файл будет # image.json - зашифрованный контент
                    not_encrypted = True
                    for encrypted_type in self.encrypted_types:
                        if os.path.isfile(os.path.join(_obj_code_dir, encrypted_type)):
                            self.code[code_name] = helper.bin_read(_obj_code_dir, encrypted_type)
                            self.header[f'code_encoding_{code_name}'] = encrypted_type
                            not_encrypted = False
                            break
                    if not_encrypted:
                        raise err from err
            else:
                code_file_name = f'{self.header["uuid"]}.{self.ext_code[code_name]}'
                self.code[code_name], encoding = self.read_raw_code(src_dir, code_file_name,
                                                                    uncomment_directive=uncomment_directive)

                self.header[f'code_info_{code_name}'] = 'file'
                self.header[f'code_encoding_{code_name}'] = encoding  # можно безболезненно поменять на utf-8-sig

    def write_decode_code(self, dest_dir, file_name):
        for code_name in self.code:
            if self.code[code_name]:
                encoding = self.header.get(f'code_encoding_{code_name}')
                if encoding in self.encrypted_types:
                    helper.bin_write(self.code[code_name], dest_dir, f'{file_name}.{code_name}.{encoding}')
                else:
                    helper.txt_write(self.code[code_name], dest_dir, f'{file_name}.{code_name}.bsl')

    def encode_code(self, src_dir, file_name):
        for code_name in self.ext_code:
            if self.header.get(f'code_info_{code_name}'):
                try:
                    encoding = self.header.get(f'code_encoding_{code_name}')
                    if encoding in self.encrypted_types:
                        self.code[code_name] = helper.bin_read(src_dir, f'{file_name}.{code_name}.{encoding}')
                    else:
                        self.code[code_name] = helper.txt_read(src_dir, f'{file_name}.{code_name}.bsl')
                except FileNotFoundError:
                    self.code[code_name] = ''

    def write_encode_code(self, dest_dir, *, comment_directive=False):
        for code_name in self.code:
            encoding = self.header.get(f'code_encoding_{code_name}', 'utf-8')
            if self.header[f'code_info_{code_name}'] == 'file':
                _code_file_name = f'{self.header["uuid"]}.{self.ext_code[code_name]}'
                self.file_list.append(_code_file_name)
                if encoding in self.encrypted_types:
                    helper.bin_write(self.code[code_name], dest_dir, _code_file_name)
                else:
                    self.write_raw_code(self.code[code_name], dest_dir, _code_file_name, encoding=encoding,
                                        comment_directive=comment_directive)
            else:
                dir_name = f'{self.header["uuid"]}.{self.ext_code[code_name]}'
                _code_dir = os.path.join(dest_dir, dir_name)
                self.file_list.append(dir_name)
                helper.makedirs(_code_dir)
                helper.brace_file_write(self.header[f'code_info_{code_name}'], _code_dir, 'info')
                if encoding in self.encrypted_types:
                    helper.bin_write(self.code[code_name], _code_dir, 'text')
                else:
                    self.write_raw_code(self.code[code_name], _code_dir, 'text', encoding=encoding,
                                        comment_directive=comment_directive)

    def set_product_version(self, product_version):
        pass

    def set_product_comment(self, product_version, product=None):
        if not product_version:
            return
        header = self.get_decode_header(self.header['header'])

        comment = helper.str_decode(header[4])
        version_index = comment.find('ver:')
        if version_index >= 0 and self.options.get('product_version'):
            new_comment = [comment[:version_index + 3], product_version]
            if product:
                new_comment.append(product)
            new_comment = ':'.join(new_comment)
            header[4] = new_comment

    def set_product_info(self, src_dir, file_name):
        product_version = self.options.get('product_version', '')
        self.set_product_version(product_version)
        if file_name:
            product_info = f'{file_name};{product_version}'
            self.set_product_comment(product_info)

    def _decode_html_data(self, src_dir, dest_dir, dest_file_name, *, header_field='html', file_number=0,
                          extension='html'):
        try:
            file_name = f'{self.header["uuid"]}.{file_number}'
            file_size = os.path.getsize(os.path.join(src_dir, file_name))
            if file_size > 1000000:  # если файл больше мегабайте не разбираем
                shutil.copy2(
                    os.path.join(src_dir, file_name),
                    os.path.join(dest_dir, f'{dest_file_name}.bin')
                )
                return
            data = helper.brace_file_read(src_dir, file_name)
        except FileNotFoundError:
            return
        try:
            if data[0][3] and data[0][3][0]:
                bin_data = self._extract_b64_data(data[0][3])
                helper.bin_write(bin_data, dest_dir, f'{dest_file_name}.{extension}')
        except IndexError:
            pass
        self.header[header_field] = data

    def _extract_b64_data(self, raw_data):
        if raw_data[0].startswith('##base64:'):
            bin_data = b64decode(raw_data[0][9:])
            raw_data[0] = '##base64:'
        elif raw_data[0].startswith('#base64:'):
            bin_data = b64decode(raw_data[0][8:])
            raw_data[0] = '#base64:'
        elif raw_data[0].startswith('#data:'):
            bin_data = b64decode(raw_data[0][6:])
            raw_data[0] = '#data:'
        else:
            raise NotImplementedError('decode_html_data')
        return bin_data

    def _encode_html_data(self, src_dir, file_name, dest_dir, *, header_field='html', file_number=0, extension='html'):
        dest_file_name = f'{self.header["uuid"]}.{file_number}'
        try:
            bin_data = helper.bin_read(src_dir, f'{file_name}.{extension}')
        except FileNotFoundError:
            try:
                shutil.copy2(
                    os.path.join(src_dir, f'{file_name}.bin'),
                    os.path.join(dest_dir, dest_file_name)
                )
                self.file_list.append(dest_file_name)
                return
            except FileNotFoundError:
                bin_data = None
        header = self.header.get(header_field)
        if header and len(header[0]) > 2 and bin_data:
            header[0][3][0] += b64encode(bin_data).decode(encoding='utf-8')
        if header:
            self.file_list.append(dest_file_name)
            helper.brace_file_write(header, dest_dir, dest_file_name)

    @staticmethod
    def _get_b64_string(bin_data):
        if not bin_data:
            return "##base64:"
        else:
            return "#base64:" + b64encode(bin_data).decode(encoding='utf-8')

    def _decode_info(self, src_dir, dest_dir, dest_file_name):
        if self._obj_info:
            for elem in self._obj_info:
                try:
                    data = helper.brace_file_read(src_dir, f'{self.header["uuid"]}.{self._obj_info[elem]}')
                    helper.json_write(data, dest_dir, f'{dest_file_name}.{self._obj_info[elem]}.json')

                except FileNotFoundError:
                    pass

    def _decode_unknown(self, src_dir, dest_dir, dest_file_name):
        if self._unknown_binary:
            for elem in self._unknown_binary:
                try:
                    shutil.copy2(
                        os.path.join(src_dir, f'{self.header["uuid"]}.{self._unknown_binary[elem]}'),
                        os.path.join(dest_dir, f'{dest_file_name}.{elem}.bin')
                    )
                except FileNotFoundError:
                    pass

    def _encode_info(self, src_dir, file_name, dest_dir):
        if self._obj_info:
            for elem in self._obj_info:
                try:
                    data = helper.json_read(src_dir, f'{file_name}.{self._obj_info[elem]}.json')
                    dest_file_name = f'{self.header["uuid"]}.{self._obj_info[elem]}'
                    helper.brace_file_write(data, dest_dir, dest_file_name)
                    self.file_list.append(dest_file_name)
                except FileNotFoundError:
                    pass
