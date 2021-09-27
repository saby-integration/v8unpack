import os
from ... import helper
from ..core.Simple import Simple

FORM83 = "13"
FORM82 = "9"
FORM81 = "7"


class Form8x(Simple):
    ver = ''
    folder = "Формы"

    def __init__(self):
        super().__init__()
        self.form = None
        self.code = None
        self.elements = None

    def decode_object(self, src_dir, uuid, dest_dir, dest_path, version, header):
        super(Form8x, self).decode_object(src_dir, uuid, dest_dir, dest_path, version, header)
        self.decode_data(src_dir, uuid)

    def write_decode_object(self, dest_dir, dest_path, version):
        super(Form8x, self).write_decode_object(dest_dir, dest_path, version)
        _dest_dir = os.path.join(dest_dir, dest_path)
        # helper.json_write(self.header, _dest_dir, f'{self.header["name"]}.json')
        helper.json_write(self.form, _dest_dir, f'{self.header["name"]}.form{self.ver}.json')
        # helper.txt_write(self.code, _dest_dir, f'{self.header["name"]}.1c')
        return []

    def decode_data(self, src_dir, uuid):
        raise NotImplemented()

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][1][1][1]

    def encode_object(self, src_dir, file_name, dest_dir, version):
        try:
            self.form = helper.json_read(src_dir, f'{file_name}.form{version}.json')
        except FileNotFoundError:
            self.form = self.encode_empty_form()
        try:
            self.code = helper.txt_read(src_dir, f'{file_name}.1c')
        except FileNotFoundError:
            self.code = ''

        self.encode_write(dest_dir)

    def encode_header(self):
        raise NotImplemented()

    def encode_data(self):
        raise NotImplemented()

    def encode_empty_form(self):
        raise NotImplemented()

    def encode_write(self, dest_dir):
        raise NotImplemented()
