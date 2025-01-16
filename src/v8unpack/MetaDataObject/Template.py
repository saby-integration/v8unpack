from ..MetaDataObject import MetaDataObject

import os
import shutil
from base64 import b64decode
from enum import Enum

from v8unpack.MetaDataObject.core.Simple import Simple
from v8unpack import helper
from v8unpack.ext_exception import ExtException, ExtNotImplemented
from v8unpack.json_container_decoder import BigBase64


class TmplType(Enum):
    table = "0"
    base64 = "1"
    active_doc = "2"
    html = "3"
    text = "4"
    geographic = "5"
    scheme = "6"
    design = "7"  # Макет оформления компоновки данных
    graphic_scheme = "8"
    extension = "9"
    # todo добавить остальные типы макетов и их сериализацию


class Template2(Simple):

    def __init__(self, *, meta_obj_class=None, obj_version=None, options=None):
        super().__init__(meta_obj_class=meta_obj_class, obj_version=obj_version, options=options)
        self.data = None
        self.tmpl_type = None
        self.raw_data = None
        self.raw_header = None

    def decode_object(self, src_dir, uuid, dest_dir, dest_path, version, header):
        try:
            super(Template2, self).decode_object(src_dir, uuid, dest_dir, dest_path, version, header)
            tmpl_type = self.get_template_type(header)
            try:
                self.tmpl_type = TmplType(tmpl_type)
            except Exception as err:
                raise ExtNotImplemented(message='Неизвестный тип макета',
                                        detail=f'{tmpl_type} у {self.name} в файле {uuid}')
            self.header['type'] = self.tmpl_type.name

            # _dest_dir = os.path.join(dest_dir, dest_path)
        except Exception as err:
            raise ExtException(parent=err)
        try:
            getattr(self, f'decode_{self.tmpl_type.name}_data')(src_dir, self.new_dest_dir, True)
        except AttributeError:
            raise Exception(f'Не реализованный тип макета {self.header["type"]}')

    # @classmethod
    # def get_decode_header(cls, header_data):
    #     return header_data[0][1][2]

    @classmethod
    def get_template_type(cls, header_data):
        return header_data[0][1][1]

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][2]

    def decode_code(self, src_dir, **kwargs):
        return

    def decode_includes(self, src_dir, dest_dir, dest_path, header):
        return []

    def decode_active_doc_data(self, src_dir, dest_dir, write):
        self.decode_scheme_data(src_dir, dest_dir, write)

    def decode_geographic_data(self, src_dir, dest_dir, write):
        self.decode_scheme_data(src_dir, dest_dir, write)

    def decode_design_data(self, src_dir, dest_dir, write):
        self.decode_scheme_data(src_dir, dest_dir, write)

    def decode_graphic_scheme_data(self, src_dir, dest_dir, write):
        self.decode_scheme_data(src_dir, dest_dir, write)

    def decode_scheme_data(self, src_dir, dest_dir, write, *, extension='bin'):
        try:
            shutil.copy2(
                os.path.join(src_dir, f'{self.header["uuid"]}.0'),
                os.path.join(self.new_dest_dir, f'{self.new_dest_file_name}.{extension}')
            )
        except FileNotFoundError:
            return
            # self.decode_text_data(src_dir, dest_dir, write) ??? что это

    def decode_table_data(self, src_dir, dest_dir, write):
        self.decode_scheme_data(src_dir, dest_dir, write, extension='mxl')

    def decode_text_data(self, src_dir, dest_dir, write):
        try:
            self.data, encoding = helper.txt_read_detect_encoding(src_dir, f'{self.header["uuid"]}.0')
        except FileNotFoundError:
            return
        if write:
            helper.txt_write(self.data, self.new_dest_dir, f'{self.new_dest_file_name}.txt', encoding=encoding)

    def decode_extension_data(self, src_dir, dest_dir, write):
        self.decode_base64_data(src_dir, dest_dir, write)

    def decode_base64_data(self, src_dir, dest_dir, write):
        filename = f'{self.header["uuid"]}.0'
        try:
            data = helper.brace_file_read(src_dir, filename)
        except BigBase64:
            shutil.copy2(os.path.join(src_dir, filename),
                         os.path.join(self.new_dest_dir, f'{self.new_dest_file_name}.c1b64'))
            return
        except FileNotFoundError:
            file_name = f'{self.header["uuid"]}.0'
            if os.path.isfile(os.path.join(src_dir, file_name)):
                # todo сюда можно вставить выдергивание бинарника из файла если кому то хочется
                shutil.copy2(
                    os.path.join(src_dir, file_name),
                    os.path.join(self.new_dest_dir, f'{self.new_dest_file_name}')
                )
            return
        if data[0][1] and data[0][1][0]:
            self.data = b64decode(data[0][1][0][8:])
            data[0][1][0] = '"данные в отдельном файле"'
            if write:
                extension = helper.get_extension_from_comment(self.header['comment'])
                helper.bin_write(self.data, self.new_dest_dir, f'{self.new_dest_file_name}.{extension}')

    def decode_html_data(self, src_dir, dest_dir, write):
        self._decode_html_data(src_dir, dest_dir, self.new_dest_file_name)

    def decode_header(self, header_data, *, id_in_separate_file=True):
        self.tmpl_type = TmplType(self.get_template_type(header_data))
        self.header = {
            'type': self.tmpl_type.name,
            'header': header_data
        }
        _header = self.get_decode_header(header_data)
        helper.decode_header(self.header, _header)
        self.uuid = self.header['uuid']
        self.name = self.header['name']

    def encode_object(self, src_dir, file_name, dest_dir):
        self.tmpl_type = TmplType[self.header['type']]

        self.raw_header = self.encode_header()
        try:
            handler = f'encode_{self.tmpl_type.name}_data'
            getattr(self, handler)(src_dir, file_name, dest_dir)
        except AttributeError:
            raise Exception(f'Не реализованный тип макета {self.header["type"]}')

        # helper.json_write(self.raw_header, dest_dir, f'{self.header["uuid"]}.bin')

    def encode_active_doc_data(self, src_dir, file_name, dest_dir):
        self.encode_scheme_data(src_dir, file_name, dest_dir)

    def encode_table_data(self, src_dir, file_name, dest_dir):
        self.encode_scheme_data(src_dir, file_name, dest_dir, extension='mxl')

    def encode_geographic_data(self, src_dir, file_name, dest_dir):
        self.encode_scheme_data(src_dir, file_name, dest_dir)

    def encode_design_data(self, src_dir, file_name, dest_dir):
        self.encode_scheme_data(src_dir, file_name, dest_dir)

    def encode_graphic_scheme_data(self, src_dir, file_name, dest_dir):
        self.encode_scheme_data(src_dir, file_name, dest_dir)

    def encode_scheme_data(self, src_dir, file_name, dest_dir, *, extension='bin'):
        try:
            dest_file_name = f'{self.header["uuid"]}.0'
            shutil.copy2(
                os.path.join(src_dir, f'{file_name}.{extension}'),
                os.path.join(dest_dir, dest_file_name)
            )
            self.file_list.append(dest_file_name)
        except FileNotFoundError:
            self.encode_text_data(src_dir, file_name, dest_dir)

    def encode_text_data(self, src_dir, file_name, dest_dir):
        try:
            raw_data, encoding = helper.txt_read_detect_encoding(src_dir, f'{file_name}.txt')
            file_name = f'{self.header["uuid"]}.0'
            helper.txt_write(raw_data, dest_dir, file_name, encoding=encoding)
            self.file_list.append(file_name)
        except FileNotFoundError:
            pass

    def encode_extension_data(self, src_dir, file_name, dest_dir):
        self.encode_base64_data(src_dir, file_name, dest_dir)

    def encode_base64_data(self, src_dir, file_name, dest_dir):
        extension = helper.get_extension_from_comment(self.header['comment'])
        try:
            bin_data = helper.bin_read(src_dir, f'{file_name}.{extension}')
            self._encode_bin_data(bin_data, dest_dir)
        except FileNotFoundError:
            file_name = f'{file_name}.c1b64'
            if os.path.isfile(os.path.join(src_dir, file_name)):
                dest_file_name = f'{self.header["uuid"]}.0'
                self.file_list.append(dest_file_name)
                shutil.copy2(
                    os.path.join(src_dir, file_name),
                    os.path.join(dest_dir, dest_file_name)
                )

    def encode_html_data(self, src_dir, file_name, dest_dir):
        self._encode_html_data(src_dir, file_name, dest_dir)

    def _encode_bin_data(self, bin_data, dest_dir):
        self.raw_data = [[
            "1",
            [self._get_b64_string(bin_data)]
        ]]

        file_name = f'{self.header["uuid"]}.0'
        helper.brace_file_write(self.raw_data, dest_dir, file_name)
        self.file_list.append(file_name)

    # def encode_header(self):
    #     # raise NotImplemented()
    #     form_header = self.get_decode_header(self.header['header'])
    #     helper.encode_header(self.header, form_header)
    #     return self.header['header']
    #
    #     header_data = self.header['header']
    #     header_data[1][1] = self.tmpl_type.value
    #
    #     return [[
    #         "1",
    #         [
    #             "2",
    #             self.tmpl_type.value,
    #             [
    #                 self.header['h0'],
    #                 [
    #                     self.header['h1_0'],
    #                     "0",
    #                     self.header['uuid']
    #                 ],
    #                 helper.str_encode(self.header['name']),
    #                 helper.encode_name2(self.header),
    #                 helper.str_encode(self.header['comment']),
    #                 *self.header['h5']
    #             ]
    #         ],
    #         "0"
    #     ]]


class Template(MetaDataObject):
    versions = {
        '2': Template2
    }
