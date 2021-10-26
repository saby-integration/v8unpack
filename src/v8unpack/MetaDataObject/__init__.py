import os

from .. import helper
from ..MetaObject import MetaObject
from ..ext_exception import ExtException


class MetaDataObject(MetaObject):
    versions = None
    version = None

    def __init__(self):
        super(MetaDataObject, self).__init__()
        self.path = ''
        self.obj_name = None

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
            tasks = self.decode_includes(src_dir, dest_dir, dest_path, header_data)
            self.write_decode_object(dest_dir, dest_path, version)
            return tasks
        except Exception as err:
            raise ExtException(
                parent=err,
                message=str(err),
                action=f'{cls.__name__}.decode'
            ) from err

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        self.set_header_data(header_data)

    def write_decode_object(self, dest_dir, dest_path, version):
        helper.json_write(self.header, os.path.join(dest_dir, dest_path), f'{self.header["name"]}.json')
        self.write_decode_code(os.path.join(dest_dir, dest_path), self.header["name"])

    @classmethod
    def encode(cls, src_dir, file_name, dest_dir, version):
        self = cls()
        self.version = version
        try:
            self.header = helper.json_read(src_dir, f'{file_name}.json')
            self.encode_object(src_dir, file_name, dest_dir, version)
            self.write_encode_object(dest_dir)
            return self.encode_includes(src_dir, dest_dir)
        except Exception as err:
            msg = f'{cls.__name__}: {err}'
            raise Exception(msg) from err

    def encode_object(self, src_dir, file_name, dest_dir, version):
        msg = f'Нет реализации для "{self.__class__.__name__}"'
        raise Exception(msg)

    def write_encode_object(self, dest_dir):
        helper.json_write(self.header['data'], dest_dir, f'{self.header["uuid"]}.json')
        self.write_encode_code(dest_dir)
