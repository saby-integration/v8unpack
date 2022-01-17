import os

from .. import helper
from ..MetaObject import MetaObject
from ..ext_exception import ExtException


class MetaDataObject(MetaObject):
    versions = None
    version = None
    _obj_name = None

    def __init__(self):
        super().__init__()
        self.path = ''
        self.new_dest_path = None
        self.new_dest_dir = None
        self.new_dest_file_name = None

    @classmethod
    def get_obj_name(cls):
        return cls._obj_name if cls._obj_name else cls.__name__

    @classmethod
    def get_version(cls, version):
        if cls.versions is None:
            return cls
        try:
            return cls.versions[version]
        except KeyError:
            raise Exception(f'Нет реализации {cls.__name__} для версии "{version}"')

    @classmethod
    def decode(cls, src_dir, file_name, dest_dir, dest_path, version):
        try:
            header_data = helper.json_read(src_dir, f'{file_name}.json')
            self = cls()
            self.version = version
            self.decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
            self.set_write_decode_mode(dest_dir, dest_path)
            tasks = self.decode_includes(src_dir, dest_dir, self.new_dest_path, header_data)
            self.write_decode_object(dest_dir, self.new_dest_path, self.new_dest_file_name, version)
            return tasks
        except ExtException as err:
            raise ExtException(
                parent=err,
                message=err.message + err.detail,
                detail=f'in decode {cls.__name__}',
                action=f'{cls.__name__}.decode'
            ) from err
        except Exception as err:
            raise ExtException(
                parent=err,
                action=f'{cls.__name__}.decode'
            ) from err

    def set_write_decode_mode(self, dest_dir, dest_path):
        self.set_mode_decode_in_root_folder(dest_dir, dest_path)

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        self.set_header_data(header_data)

    def write_decode_object(self, dest_dir, dest_path, file_name, version):
        dest_full_path = os.path.join(dest_dir, dest_path)
        helper.json_write(self.header, dest_full_path, f'{file_name}.json')
        self.write_decode_code(dest_full_path, file_name)

    def set_mode_decode_in_name_folder(self, dest_dir, dest_path):
        self.new_dest_path = os.path.join(dest_path, self.header['name'])
        self.new_dest_dir = os.path.join(dest_dir, self.new_dest_path)
        self.new_dest_file_name = self.get_obj_name()
        os.makedirs(self.new_dest_dir)

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
            self.write_encode_object(dest_dir)
            return self.encode_includes(src_dir, dest_dir)
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
        helper.json_write(self.header['data'], dest_dir, f'{self.header["uuid"]}.json')
        self.write_encode_code(dest_dir)
