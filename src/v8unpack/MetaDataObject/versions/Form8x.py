import os
import re

from ..core.Simple import SimpleNameFolder
from ... import helper
from ...ext_exception import ExtException


class Form8x(SimpleNameFolder):
    ver = ''
    _obj_name = "Form"
    double_quotes = re.compile(r'("")')
    quotes = re.compile(r'(")')

    def __init__(self):
        super().__init__()
        self.form = []
        self.elements = []
        self.props = []

    def decode_object(self, src_dir, uuid, dest_dir, dest_path, version, header_data):
        self.set_header_data(header_data)
        self.set_write_decode_mode(dest_dir, dest_path)
        self.decode_data(src_dir, uuid)
        self.decode_code(src_dir)

    def decode_form0(self, src_dir, uuid):
        try:
            form = helper.brace_file_read(src_dir, f'{uuid}.0')
        except FileNotFoundError:
            self.form.append([])
            return
        try:
            _code = helper.str_decode(self.getset_form_code(form, 'Код в отдельном файле', self.header))
            if _code is not None:
                _code = self.double_quotes.sub(r'"', _code)
                self.code['obj'] = _code
                self.header['code_info_obj'] = 'Код в отдельном файле'
        except Exception as err:
            raise ExtException(parent=err, detail=self.header['uuid'])
        self.form.append(form)

    @classmethod
    def getset_form_code(cls, form, new_value=None, header=None):
        err_detail = f'{header["uuid"]} {header["name"]} ' \
                     f'опытным путем подобрано, если у Вас код не достается' \
                     f'обновитесь до последней версии, и если не поможет создайте issue с дампом'
        len_form_0 = len(form[0])
        if len_form_0 > 2 and form[0][0] in ['4', '3', '2']:
            code = form[0][2]
            if not isinstance(code, str):
                raise ExtException(
                    message='Not supported forms',
                    detail=err_detail,
                    dump=form
                )
            form[0][2] = new_value
            if len_form_0 != 10:
                a = 1
            return code

        last_level = cls.get_last_level_array(form)
        if len_form_0 < 10 and (last_level[0] == '49' or last_level[0] == '4'):
            return ''

        if len(last_level) > 10 \
                and last_level[0] in ['22', '1'] \
                and last_level[-1] == '0' \
                and last_level[-2] == '0':
            code_index = -8
            code = last_level[code_index]
            if not isinstance(code, str):
                raise ExtException(
                    message='Not supported forms',
                    detail=err_detail,
                    dump=form
                )
            if new_value is not None:
                last_level[code_index] = new_value
            return code
        return ''

    def decode_old_form(self, src_dir):
        file_name = f'{self.header["uuid"]}.0'
        _code_dir = os.path.join(src_dir, file_name)
        if os.path.exists(_code_dir):
            if os.path.isdir(_code_dir):
                self.form.append(helper.brace_file_read(_code_dir, 'form'))
                try:
                    encoding = helper.detect_by_bom(os.path.join(_code_dir, 'module'), 'utf-8')
                    self.code['obj'] = self.read_raw_code(_code_dir, 'module', encoding=encoding)
                except UnicodeDecodeError:
                    encoding = 'windows-1251'
                    self.code['obj'] = self.read_raw_code(_code_dir, 'module', encoding=encoding)
                self.header['code_encoding_obj'] = encoding  # можно безболезненно поменять на utf-8-sig
                self.header[f'code_info_obj'] = 1
            else:
                self.decode_form0(src_dir, self.header["uuid"])
                pass

    def write_decode_object(self, dest_dir, dest_path, file_name, version):
        super(Form8x, self).write_decode_object(dest_dir, dest_path, file_name, version)
        helper.json_write(self.form, self.new_dest_dir, f'{file_name}.form{version}.json')
        if self.elements:
            helper.json_write(self.elements, self.new_dest_dir, f'{file_name}.elements{version}.json')
        if self.props:
            helper.json_write(self.props, self.new_dest_dir, f'{file_name}.props{version}.json')
        return []

    def decode_data(self, src_dir, uuid):
        raise NotImplemented()

    def get_decode_header(self, header):
        return self.get_decode_obj_header(header)[1][1]

    def get_decode_obj_header(self, header_data):
        return header_data[0][1] if self.obj_version == '0' else header_data[0][1][1]

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
        helper.brace_file_write(self.encode_header(), dest_dir, f'{self.header["uuid"]}')
        if self.header.get('code_info_obj'):
            _code_dir = f'{os.path.join(dest_dir, self.header["uuid"])}.0'
            helper.makedirs(_code_dir, exist_ok=True)
            helper.brace_file_write(self.form[0], _code_dir, 'form')
            _encoding = self.header.get('code_encoding_obj', 'utf-8-sig')
            self.write_raw_code(self.code.get('obj', ''), _code_dir, 'module', encoding=_encoding)

    @classmethod
    def get_last_level_array(cls, data):
        while True:
            if isinstance(data[-1], list):
                return cls.get_last_level_array(data[-1])
            else:
                return data
