import os
from ...MetaDataObject import MetaDataObject
from .. import helper


class Container(MetaDataObject):
    def __init__(self):
        super(Container, self).__init__()
        self.new_dest_path = None
        self.new_dest_dir = None

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super(Container, self).decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        self.decode_code(src_dir)
        self.new_dest_path = os.path.join(dest_path, self.header['name'])
        self.new_dest_dir = os.path.join(dest_dir, self.new_dest_path)
        os.makedirs(self.new_dest_dir)

    def write_decode_object(self, dest_dir, dest_path, version):
        helper.json_write(self.header, self.new_dest_dir, f'{self.__class__.__name__}.json')
        if self.code:
            helper.txt_write(self.code, self.new_dest_dir, f'{self.__class__.__name__}.1c')

    def decode_includes(self, src_dir, dest_dir, dest_path, header_data):
        return super(Container, self).decode_includes(src_dir, dest_dir, self.new_dest_path, header_data)

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][1]

    def encode_object(self, src_dir, file_name, dest_dir, version):
        helper.json_write(self.header['data'], dest_dir, f'{self.header["uuid"]}.json')
        self.encode_code(src_dir, dest_dir)
        return []
