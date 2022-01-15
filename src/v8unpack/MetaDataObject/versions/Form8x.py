import os

from ..core.Simple import SimpleNameFolder
from ... import helper

FORM83 = "13"
FORM82 = "9"
FORM81 = "7"


class Form8x(SimpleNameFolder):
    ver = ''
    _obj_name = "Form"

    def __init__(self):
        super().__init__()
        self.form = []
        self.elements = None

    def decode_object(self, src_dir, uuid, dest_dir, dest_path, version, header_data):
        self.set_header_data(header_data)
        self.decode_data(src_dir, uuid)
        self.decode_code(src_dir)

    def decode_old_form(self, src_dir):
        _code_dir = f'{os.path.join(src_dir, self.header["uuid"])}.0'
        if os.path.isdir(_code_dir):
            self.form.append(helper.json_read(_code_dir, 'form.json'))
            try:
                encoding = helper.detect_by_bom(os.path.join(_code_dir, 'module.txt'), 'utf-8')
                self.code['obj'] = self.read_raw_code(_code_dir, 'module.txt', encoding=encoding)
            except UnicodeDecodeError:
                encoding = 'windows-1251'
                self.code['obj'] = self.read_raw_code(_code_dir, 'module.txt', encoding=encoding)
            self.header['code_encoding_obj'] = encoding  # можно безболезненно поменять на utf-8-sig
            self.header[f'code_info_obj'] = 1

    def write_decode_object(self, dest_dir, dest_path, file_name, version):
        super(Form8x, self).write_decode_object(dest_dir, dest_path, file_name, version)
        helper.json_write(self.form, self.new_dest_dir, f'{file_name}.form{self.ver}.json')
        return []

    def decode_data(self, src_dir, uuid):
        raise NotImplemented()

    @classmethod
    def get_decode_header(cls, header):
        return cls.get_decode_obj_header(header)[1][1]

    @classmethod
    def get_decode_obj_header(cls, header):
        return header[0][1][1]

    def encode_object(self, src_dir, file_name, dest_dir, version):
        super(Form8x, self).encode_object(src_dir, file_name, dest_dir, version)
        try:
            self.form = helper.json_read(src_dir, f'{file_name}.form{version}.json')
        except FileNotFoundError:
            self.form = self.encode_empty_form()
        self.encode_data()

    def encode_header(self):
        raise NotImplemented()

    def encode_data(self):
        raise NotImplemented()

    def encode_empty_form(self):
        raise NotImplemented()

    def encode_write(self, dest_dir):
        raise NotImplemented()

    def write_encode_code(self, dest_dir):
        pass

    def write_old_encode_object(self, dest_dir):
        helper.json_write(self.encode_header(), dest_dir, f'{self.header["uuid"]}.json')
        if self.header.get('code_info_obj'):
            _code_dir = f'{os.path.join(dest_dir, self.header["uuid"])}.0'
            os.makedirs(_code_dir, exist_ok=True)
            helper.json_write(self.form[0], _code_dir, 'form.json')
            _encoding = self.header.get('code_encoding_obj', 'utf-8-sig')
            self.write_raw_code(self.code.get('obj', ''), _code_dir, 'module.txt', encoding=_encoding)
