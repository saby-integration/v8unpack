import os
from ...MetaDataObject import MetaDataObject
from .. import helper


class Simple(MetaDataObject):
    def __init__(self):
        super(Simple, self).__init__()
        self.code = None

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super(Simple, self).decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        self.decode_code(src_dir)

    def write_decode_object(self, dest_dir, dest_path, version):
        super(Simple, self).write_decode_object(dest_dir, dest_path, version)
        helper.txt_write(self.code, os.path.join(dest_dir, dest_path), f'{self.header["name"]}.1c')

    def decode_includes(self, src_dir, dest_dir, dest_path, header):
        return []

    def encode_includes(self, src_dir, dest_dir):
        return []

    def encode_object(self, src_dir, file_name, dest_dir, version):
        helper.json_write(self.header['data'], dest_dir, f'{self.header["uuid"]}.json')
        self.encode_code(src_dir, dest_dir)
        return []
