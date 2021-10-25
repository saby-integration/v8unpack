import os
from base64 import b64decode, b64encode
from enum import Enum

from ..core.Simple import Simple
from ... import helper


class TmplType(Enum):
    table = "0"
    base64 = "1"
    html = "3"
    text = "4"
    scheme = "6"
    extension = "9"
    # todo добавить остальные типы макетов и их сериализацию


class Template8x(Simple):
    folder = "Макеты"

    def __init__(self):
        super().__init__()
        self.data = None
        self.tmpl_type = None
        self.raw_data = None
        self.raw_header = None

    @property
    def uuid(self):
        if self.header:
            return self.header['uuid']
        return None

    def decode_object(self, src_dir, uuid, dest_dir, dest_path, version, header):
        super(Template8x, self).decode_object(src_dir, uuid, dest_dir, dest_path, version, header)
        self.tmpl_type = TmplType(self.get_template_type(header))
        self.header['type'] = self.tmpl_type.name

        _dest_dir = os.path.join(dest_dir, dest_path)
        try:
            getattr(self, f'decode_{self.tmpl_type.name}_data')(src_dir, _dest_dir, True)
        except AttributeError:
            raise Exception(f'Не реализованный тип макета {self.header["type"]}')

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][2]

    @classmethod
    def get_template_type(cls, header_data):
        return header_data[0][1][1]

    def decode_code(self, src_dir):
        return

    def decode_includes(self, src_dir, dest_dir, dest_path, header):
        return []

    def decode_scheme_data(self, src_dir, dest_dir, write):
        try:
            self.data = helper.bin_read(src_dir, f'{self.header["uuid"]}.0.bin')
        except FileNotFoundError:
            return
        if write:
            helper.bin_write(self.data, dest_dir, f'{self.header["name"]}.bin')

    def decode_table_data(self, src_dir, dest_dir, write):
        self.decode_text_data(src_dir, dest_dir, write)

    def decode_text_data(self, src_dir, dest_dir, write):
        try:
            self.data, encoding = helper.txt_read_detect_encoding(src_dir, f'{self.header["uuid"]}.0.txt')
        except FileNotFoundError:
            return
        if write:
            helper.txt_write(self.data, dest_dir, f'{self.header["name"]}.txt', encoding=encoding)

    def decode_extension_data(self, src_dir, dest_dir, write):
        self.decode_base64_data(src_dir, dest_dir, write)

    def decode_base64_data(self, src_dir, dest_dir, write):
        try:
            data = helper.json_read(src_dir, f'{self.header["uuid"]}.0.json')
        except FileNotFoundError:
            return
        if data[0][1] and data[0][1][0]:
            self.data = b64decode(data[0][1][0][8:])
            data[0][1][0] = '"данные в отдельном файле"'
            extension = helper.get_extension_from_comment(self.header['comment'])
            if write:
                helper.bin_write(self.data, dest_dir, f'{self.header["name"]}.{extension}')

    def decode_html_data(self, src_dir, dest_dir, write):
        try:
            data = helper.json_read(src_dir, f'{self.header["uuid"]}.0.json')
        except FileNotFoundError:
            return
        if data[0][3] and data[0][3][0]:
            self.data = b64decode(data[0][3][0][8:])
            data[0][3][0] = '"данные в отдельном файле"'
            if write:
                helper.bin_write(self.data, dest_dir, f'{self.header["name"]}.html')

    def decode_header(self, header):
        self.tmpl_type = TmplType(header[0][1][1])
        self.header = {
            'type': self.tmpl_type.name,
        }
        _header = header[0][1][2]
        helper.decode_header(self.header, _header)

    def encode_object(self, src_dir, file_name, dest_dir, version):
        self.tmpl_type = TmplType[self.header['type']]

        self.raw_header = self.encode_header()
        try:
            handler = f'encode_{self.tmpl_type.name}_data'
            getattr(self, handler)(src_dir, dest_dir)
        except AttributeError:
            raise Exception(f'Не реализованный тип макета {self.header["type"]}')

        helper.json_write(self.raw_header, dest_dir, f'{self.header["uuid"]}.json')

    def encode_table_data(self, src_dir, dest_dir):
        self.encode_text_data(src_dir, dest_dir)

    def encode_scheme_data(self, src_dir, dest_dir):
        try:
            raw_data = helper.bin_read(src_dir, f'{self.header["name"]}.bin')
            helper.bin_write(raw_data, dest_dir, f'{self.header["uuid"]}.0.bin')
        except FileNotFoundError:
            pass

    def encode_text_data(self, src_dir, dest_dir):
        try:
            raw_data, encoding = helper.txt_read_detect_encoding(src_dir, f'{self.header["name"]}.txt')
            helper.txt_write(raw_data, dest_dir, f'{self.header["uuid"]}.0.txt', encoding=encoding)
        except FileNotFoundError:
            pass

    def encode_extension_data(self, src_dir, dest_dir):
        self.encode_base64_data(src_dir, dest_dir)

    def encode_base64_data(self, src_dir, dest_dir):
        extension = helper.get_extension_from_comment(self.header['comment'])
        bin_data = helper.bin_read(src_dir, f'{self.header["name"]}.{extension}')
        self._encode_bin_data(bin_data, dest_dir)

    def encode_html_data(self, src_dir, dest_dir):
        bin_data = helper.bin_read(src_dir, f'{self.header["name"]}.html')
        self.raw_data = [[
            "5",
            "1",
            "\"ru\"",
            ["#base64:" + b64encode(bin_data).decode(encoding='utf-8')],
            "0"
        ]]
        helper.json_write(self.raw_data, dest_dir, f'{self.header["uuid"]}.0.json')

    def _encode_bin_data(self, bin_data, dest_dir):
        self.raw_data = [[
            "1",
            ["#base64:" + b64encode(bin_data).decode(encoding='utf-8')]
        ]]
        helper.json_write(self.raw_data, dest_dir, f'{self.header["uuid"]}.0.json')

    def encode_header(self):
        raise NotImplemented()
