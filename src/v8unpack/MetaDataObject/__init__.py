import os

from .. import helper
from ..MetaObject import MetaObject
from ..ext_exception import ExtException


class MetaDataObject(MetaObject):
    versions = None
    version = None
    _obj_name = None
    help_file_number = None

    def __init__(self):
        super().__init__()
        self.path = ''
        self.title = self.__class__.__name__
        self.new_dest_path = None
        self.new_dest_dir = None
        self.new_dest_file_name = None
        self.obj_version = None

    @classmethod
    def get_obj_name(cls):
        return cls._obj_name if cls._obj_name else cls.__name__

    @classmethod
    def get_version(cls, version):
        if cls.versions is None:
            return cls
        try:
            return cls.versions[version]
            # return cls.versions.get(version, cls.versions['803'])
        except KeyError:
            raise Exception(f'Нет реализации {cls.__name__} для версии "{version}"')

    @staticmethod
    def brace_file_read(src_dir, file_name):
        return helper.brace_file_read(src_dir, file_name)

    @classmethod
    def decode_get_handler(cls, src_dir, file_name, version):
        return cls.get_version(version)()

    @classmethod
    def decode(cls, src_dir, file_name, dest_dir, dest_path, version, *, parent_type=None):
        try:
            self = cls.decode_get_handler(src_dir, file_name, version)
            header_data = cls.brace_file_read(src_dir, file_name)
            # self = cls()
            if parent_type:
                self.title = parent_type
            self.version = version
            self.decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
            tasks = self.decode_includes(src_dir, dest_dir, self.new_dest_path, header_data)
            self.write_decode_object(dest_dir, self.new_dest_path, self.new_dest_file_name, version)
            return tasks
        except Exception as err:
            problem_file = os.path.join(os.path.basename(src_dir), file_name)
            raise ExtException(
                parent=err,
                message="Ошибка декодирования",
                detail=f'объекта метаданных "{cls.__name__}" файл "{problem_file}" ({dest_path})',
                action=f'{cls.__name__}.decode'
            ) from err

    def set_write_decode_mode(self, dest_dir, dest_path):
        self.set_mode_decode_in_root_folder(dest_dir, dest_path)

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        self.set_header_data(header_data)
        self.set_write_decode_mode(dest_dir, dest_path)

    def write_decode_object(self, dest_dir, dest_path, file_name, version):
        dest_full_path = os.path.join(dest_dir, dest_path)
        helper.json_write(self.header, dest_full_path, f'{file_name}.json')
        self.write_decode_code(dest_full_path, file_name)

    def set_mode_decode_in_name_folder(self, dest_dir, dest_path):
        self.new_dest_path = os.path.join(dest_path, self.header['name'])
        self.new_dest_dir = os.path.join(dest_dir, self.new_dest_path)
        self.new_dest_file_name = self.get_obj_name()
        helper.makedirs(self.new_dest_dir)

    def set_mode_decode_in_root_folder(self, dest_dir, dest_path):
        self.new_dest_path = dest_path
        self.new_dest_dir = os.path.join(dest_dir, self.new_dest_path)
        self.new_dest_file_name = self.header['name']

    @classmethod
    def encode(cls, src_dir, file_name, dest_dir, version):
        self = cls()
        self.version = version
        file_name = self.get_encode_file_name(file_name)
        try:
            try:
                self.header = helper.json_read(src_dir, f'{file_name}.json')
            except FileNotFoundError:
                return
            self.encode_object(src_dir, file_name, dest_dir, version)
            tasks = self.encode_includes(src_dir, file_name, dest_dir, version)
            self.write_encode_object(dest_dir)
            return tasks
        except Exception as err:
            raise ExtException(
                parent=err,
                dump=dict(src_dir=src_dir, file_name=file_name),
                action=f'{cls.__name__}.encode') from err

    @classmethod
    def get_encode_file_name(cls, file_name):
        return file_name

    def encode_object(self, src_dir, file_name, dest_dir, version):
        msg = f'Нет реализации для "{self.__class__.__name__}"'
        raise Exception(msg)

    def write_encode_object(self, dest_dir):
        helper.brace_file_write(self.header['data'], dest_dir, f'{self.header["uuid"]}')
        self.write_encode_code(dest_dir)

    @staticmethod
    def get_metadata_object_version(path, file_name):
        _path = os.path.join(path, file_name)
        with open(_path, 'r', encoding='utf-8-sig') as file:
            header = file.read(9)
            root = header.split('{')
            if len(root) < 3 or root[1][0] != '1':
                raise ExtException(message='Неизвестная версия объекта метаданных',
                                   detail=file_name)
            root = root[2].split(',')
            return int(root[0])
