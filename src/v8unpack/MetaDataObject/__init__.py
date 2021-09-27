import os
from .. import helper
from ..MetaObject import MetaObject


class MetaDataObject(MetaObject):
    versions = None
    version = None

    def __init__(self):
        super(MetaDataObject, self).__init__()
        self.path = ''
        self.code = None
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
            self.write_decode_object(dest_dir, dest_path, version)
            return self.decode_includes(src_dir, dest_dir, dest_path, header_data)
        except Exception as err:
            raise Exception(f'{cls.__name__} {err}') from err

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        self.set_header_data(header_data)

    def write_decode_object(self, dest_dir, dest_path, version):
        helper.json_write(self.header, os.path.join(dest_dir, dest_path), f'{self.header["name"]}.json')

    def decode_code(self, src_dir):
        _code_dir = f'{os.path.join(src_dir, self.header["uuid"])}.0'
        if os.path.isdir(_code_dir):
            self.header['info'] = helper.json_read(_code_dir, 'info.json')
            self.code = self.read_raw_code(_code_dir, 'text.txt')

    @classmethod
    def encode(cls, src_dir, file_name, dest_dir, version):
        self = cls()
        self.version = version
        try:
            self.header = helper.json_read(src_dir, f'{file_name}.json')
            self.encode_object(src_dir, file_name, dest_dir, version)
            return self.encode_includes(src_dir, dest_dir)
        except Exception as err:
            msg = f'{cls.__name__}: {err}'
            raise Exception(msg) from err

    def encode_object(self, src_dir, file_name, dest_dir, version):
        msg = f'Нет реализации для "{self.__class__.__name__}"'
        raise Exception(msg)

    def encode_code(self, src_dir, dest_dir):
        if self.header.get('info'):
            self.code = helper.txt_read(src_dir, f'{self.header["name"]}.1c')

            _code_dir = f'{os.path.join(dest_dir, self.header["uuid"])}.0'
            os.makedirs(_code_dir)
            helper.json_write(self.header['info'], _code_dir, 'info.json')
            self.write_raw_code(self.code, _code_dir, 'text.txt')
