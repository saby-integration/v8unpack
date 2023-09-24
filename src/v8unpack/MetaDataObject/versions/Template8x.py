import os
import shutil
from base64 import b64decode
from enum import Enum

from ..core.Simple import Simple
from ... import helper
from ...ext_exception import ExtException


class TmplType(Enum):
    table = "0"
    base64 = "1"
    html = "3"
    text = "4"
    geographic = "5"
    scheme = "6"
    design = "7"  # Макет оформления компоновки данных
    extension = "9"
    # todo добавить остальные типы макетов и их сериализацию


class Template8x(Simple):

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
        try:
            super(Template8x, self).decode_object(src_dir, uuid, dest_dir, dest_path, version, header)
            self.tmpl_type = TmplType(self.get_template_type(header))
            self.header['type'] = self.tmpl_type.name

            _dest_dir = os.path.join(dest_dir, dest_path)
        except Exception as err:
            raise ExtException(parent=err)
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

    def decode_geographic_data(self, src_dir, dest_dir, write):
        self.decode_scheme_data(src_dir, dest_dir, write)

    def decode_design_data(self, src_dir, dest_dir, write):
        self.decode_scheme_data(src_dir, dest_dir, write)

    def decode_scheme_data(self, src_dir, dest_dir, write):
        try:
            self.data = helper.bin_read(src_dir, f'{self.header["uuid"]}.0.bin')
            if write:
                helper.bin_write(self.data, dest_dir, f'{self.header["name"]}.bin')
        except FileNotFoundError:
            self.decode_text_data(src_dir, dest_dir, write)

    def decode_table_data(self, src_dir, dest_dir, write):
        self.decode_scheme_data(src_dir, dest_dir, write)

    def decode_text_data(self, src_dir, dest_dir, write):
        try:
            self.data, encoding = helper.txt_read_detect_encoding(src_dir, f'{self.header["uuid"]}.0.bin')
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
            file_name = f'{self.header["uuid"]}.0.c1b64'
            if os.path.isfile(os.path.join(src_dir, file_name)):
                # todo сюда можно вставить выдергивание бинарника из файла если кому то хочется
                shutil.copy2(
                    os.path.join(src_dir, file_name),
                    os.path.join(dest_dir, f'{self.header["name"]}.c1b64')
                )
            return
        if data[0][1] and data[0][1][0]:
            self.data = b64decode(data[0][1][0][8:])
            data[0][1][0] = '"данные в отдельном файле"'
            if write:
                extension = helper.get_extension_from_comment(self.header['comment'])
                helper.bin_write(self.data, dest_dir, f'{self.header["name"]}.{extension}')

    def decode_html_data(self, src_dir, dest_dir, write):
        self._decode_html_data(src_dir, dest_dir, self.new_dest_file_name)

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

        # helper.json_write(self.raw_header, dest_dir, f'{self.header["uuid"]}.bin')

    def encode_table_data(self, src_dir, dest_dir):
        self.encode_scheme_data(src_dir, dest_dir)

    def encode_geographic_data(self, src_dir, dest_dir):
        self.encode_scheme_data(src_dir, dest_dir)

    def encode_design_data(self, src_dir, dest_dir):
        self.encode_scheme_data(src_dir, dest_dir)

    def encode_scheme_data(self, src_dir, dest_dir):
        try:
            raw_data = helper.bin_read(src_dir, f'{self.header["name"]}.bin')
            helper.bin_write(raw_data, dest_dir, f'{self.header["uuid"]}.0.bin')
        except FileNotFoundError:
            self.encode_text_data(src_dir, dest_dir)

    def encode_text_data(self, src_dir, dest_dir):
        try:
            raw_data, encoding = helper.txt_read_detect_encoding(src_dir, f'{self.header["name"]}.txt')
            helper.txt_write(raw_data, dest_dir, f'{self.header["uuid"]}.0.bin', encoding=encoding)
        except FileNotFoundError:
            pass

    def encode_extension_data(self, src_dir, dest_dir):
        self.encode_base64_data(src_dir, dest_dir)

    def encode_base64_data(self, src_dir, dest_dir):
        extension = helper.get_extension_from_comment(self.header['comment'])
        try:
            bin_data = helper.bin_read(src_dir, f'{self.header["name"]}.{extension}')
            self._encode_bin_data(bin_data, dest_dir)
        except FileNotFoundError:
            file_name = f'{self.header["name"]}.c1b64'
            if os.path.isfile(os.path.join(src_dir, file_name)):
                shutil.copy2(
                    os.path.join(src_dir, file_name),
                    os.path.join(dest_dir, f'{self.header["uuid"]}.0.c1b64')
                )

    def encode_html_data(self, src_dir, dest_dir):
        self._encode_html_data(src_dir, self.header["name"], dest_dir)

    def _encode_bin_data(self, bin_data, dest_dir):
        self.raw_data = [[
            "1",
            [self._get_b64_string(bin_data)]
        ]]
        helper.json_write(self.raw_data, dest_dir, f'{self.header["uuid"]}.0.json')

    def encode_header(self):
        raise NotImplemented()
