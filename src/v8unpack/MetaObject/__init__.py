import os
import re
from .. import helper
from ..metadata_types import MetaDataTypes


class MetaObject:
    version = '83'
    re_meta_data_obj = re.compile(r'^[^.]+\.json$')
    directive_1c_uncomment = re.compile('(?P<n>\\n)(?P<d>[#|&])')
    directive_1c_comment = re.compile('(?P<n>\\n)(?P<c>// v8unpack )(?P<d>[#|&])')

    def __init__(self):
        self.header = {}

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][1]

    def set_header_data(self, header_data):
        _form_header = self.get_decode_header(header_data)
        helper.decode_header(self.header, _form_header)
        self.header['data'] = header_data

    def decode_includes(self, src_dir, dest_dir, dest_path, header_data):
        tasks = []
        includes = self.get_decode_includes(header_data)
        for include in includes:
            count_include_types = int(include[2])
            for i in range(count_include_types):
                _metadata = include[i + 3]
                _count_obj = int(_metadata[1])
                _metadata_type_uuid = _metadata[0]
                if not _count_obj:
                    continue
                try:
                    metadata_type = MetaDataTypes(_metadata_type_uuid)
                except ValueError:
                    # data = helper.json_read(src_dir, f'{_metadata[2]}.json')  # чтобы посмотреть что это
                    # continue
                    msg = f'Неизестный тип метаданных {_metadata_type_uuid} в файле {_metadata[2]}'
                    raise Exception(msg)

                new_dest_path = os.path.join(dest_path, metadata_type.name)
                for j in range(_count_obj):
                    obj_uuid = _metadata[j + 2]
                    if isinstance(obj_uuid, str):
                        if j == 0:
                            os.mkdir(os.path.join(dest_dir, new_dest_path))

                        tasks.append([metadata_type.name, [src_dir, obj_uuid, dest_dir, new_dest_path, self.version]])
                    elif isinstance(obj_uuid, list):
                        continue  # можно вставить разбор Реквизитов

        return tasks

    @classmethod
    def get_decode_includes(cls, header_data: list) -> list:
        raise Exception(f'Не метаданных {cls.__name__} не указана ссылка на includes')

    def encode_includes(self, src_dir, dest_dir):
        tasks = []
        includes = self.get_encode_includes(src_dir)
        for include in includes:
            entries = os.listdir(os.path.join(src_dir, include))
            for entry in entries:
                new_src_dir = os.path.join(src_dir, include)
                if self.re_meta_data_obj.fullmatch(entry):
                    tasks.append([include, [new_src_dir, entry[:-5], dest_dir, self.version]])
                    continue
                if os.path.isdir(os.path.join(new_src_dir, entry)):
                    new_src_dir = os.path.join(new_src_dir, entry)
                    tasks.append([include, [new_src_dir, include, dest_dir, self.version]])
                    continue
        return tasks

    @classmethod
    def get_encode_includes(cls, src_dir: str) -> list:
        includes = []
        entries = sorted(os.listdir(src_dir))
        for entry in entries:
            src_entry_path = os.path.join(src_dir, entry)
            if os.path.isdir(src_entry_path):
                try:
                    MetaDataTypes[entry]
                except KeyError:
                    raise Exception(f'Обнаружен не поддерживаемый тип метаданных {entry}')
                includes.append(entry)
        return includes

    @classmethod
    def encode_version(cls):
        return [[
            [
                "216",
                "0",
                [
                    "80314",
                    "0"
                ]
            ]
        ]]

    @classmethod
    def get_class_name_without_version(cls):
        if cls.__name__.endswith(cls.version):
            return cls.__name__[:len(cls.version) * -1]
        return cls.__name__

    def read_raw_code(self, src_dir, file_name):
        code = helper.txt_read(src_dir, file_name)
        if code:
            if self.version in ['81', '82']:  # убираем комментрии у директив
                code = self.directive_1c_comment.sub('\g<n>\g<d>', code)
        return code

    def write_raw_code(self, code, dest_dir, filename):
        if code:
            if self.version in ['81', '82']:  # комментируем директивы
                code = self.directive_1c_uncomment.sub('\g<n>// v8unpack \g<d>', code)
            helper.txt_write(code, dest_dir, filename)
