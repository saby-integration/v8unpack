import os
import re

from ..core.Simple import Simple
from ... import helper

FORM83 = "13"
FORM82 = "9"
FORM81 = "7"

FORM_OF = "0"
FORM_UF = "1"


class Form8x(Simple):
    ver = ''
    folder = "Формы"
    double_quotes = re.compile('("")')
    quotes = re.compile('(")')

    def __init__(self):
        super().__init__()
        self.form = None
        self.elements = None

    def decode_object(self, src_dir, uuid, dest_dir, dest_path, version, header_data):
        self.set_header_data(header_data)
        _header_obj = self.get_decode_obj_header(self.header['data'])
        self.header['Включать в содержание справки'] = _header_obj[1][2]
        self.header['ТипФормы'] = _header_obj[1][3]
        try:
            self.header['Расширенное представление'] = _header_obj[2]
            self.header['Пояснение'] = _header_obj[3]
            self.header['Использовать стандартные команды'] = _header_obj[4]
        except IndexError:
            pass

        if self.header['ТипФормы'] == FORM_OF:
            self.decode_of(src_dir, uuid, dest_dir, dest_path, version, header_data)
        else:
            self.decode_uf(src_dir, uuid, dest_dir, dest_path, version, header_data)

    def decode_uf(self, src_dir, uuid, dest_dir, dest_path, version, header_data):
        self.form = helper.json_read(src_dir, f'{uuid}.0.json')
        self.decode_code(src_dir)
        try:
            _code = helper.str_decode(self.form[0][2])
            if _code:
                _code = self.double_quotes.sub('"', _code)
                self.code['obj'] = _code
                self.header['code_info_obj'] = 'Код в отдельном файле'
                self.form[0][2] = 'Код в отдельном файле'
        except IndexError:
            pass  # todo код расширения не достается

    def decode_of(self, src_dir, uuid, dest_dir, dest_path, version, header_data):
        _code_dir = f'{os.path.join(src_dir, self.header["uuid"])}.0'
        if os.path.isdir(_code_dir):
            self.form = helper.json_read(_code_dir, 'form.json')
            try:
                encoding = helper.detect_by_bom(os.path.join(_code_dir, 'module.txt'), 'utf-8')
                self.code['obj'] = self.read_raw_code(_code_dir, 'module.txt', encoding=encoding)
            except UnicodeDecodeError:
                encoding = 'windows-1251'
                self.code['obj'] = self.read_raw_code(_code_dir, 'module.txt', encoding=encoding)
            self.header['code_encoding_obj'] = encoding  # можно безболезненно поменять на utf-8-sig
            self.header[f'code_info_obj'] = 1

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

    def encode_empty_form(self):
        raise NotImplemented()

    def encode_write(self, dest_dir):
        raise NotImplemented()

    def write_encode_code(self, dest_dir):
        pass

    def encode_data(self):
        if self.header['ТипФормы'] == FORM_OF:
            return self.form
        try:
            _code = self.code.pop('obj', "")
            _code = self.quotes.sub('""', _code)
            self.form[0][2] = helper.str_encode(_code)
        except IndexError:
            pass
        return self.form

    def write_encode_object(self, dest_dir):
        if self.header['ТипФормы'] == FORM_OF:
            self.write_encode_object_of(dest_dir)
        else:
            helper.json_write(self.encode_header(), dest_dir, f'{self.header["uuid"]}.json')
            helper.json_write(self.form, dest_dir, f'{self.header["uuid"]}.0.json')

    def write_encode_object_of(self, dest_dir):
        helper.json_write(self.encode_header(), dest_dir, f'{self.header["uuid"]}.json')
        if self.header.get('code_info_obj'):
            _code_dir = f'{os.path.join(dest_dir, self.header["uuid"])}.0'
            os.makedirs(_code_dir, exist_ok=True)
            helper.json_write(self.form, _code_dir, 'form.json')
            _encoding = self.header.get('code_encoding_obj', 'utf-8-sig')
            self.write_raw_code(self.code['obj'], _code_dir, 'module.txt', encoding=_encoding)
