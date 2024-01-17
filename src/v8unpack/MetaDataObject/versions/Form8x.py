import os
import re

from .Form802Elements.FormElement import FormElement as FormElement802, FormProps as FormProps802
from .Form803Elements.FormElement import FormElement as FormElement803, calc_offset
from .Form802Elements.Form27 import Form27
from ..core.Simple import SimpleNameFolder
from ... import helper
from ...ext_exception import ExtException

OF = '0'  # обычные формы
UF = '1'  # управляемые формы


class Form8x(SimpleNameFolder):
    _obj_name = "Form"
    double_quotes = re.compile(r'("")')
    quotes = re.compile(r'(")')

    def __init__(self, *, obj_name=None, options=None):
        super().__init__(obj_name=obj_name, options=options)
        self.form = []
        self.elements_tree = []
        self.elements_data = {}
        self.props_index = {}
        self.props = []
        self.params = []
        self.commands = []
        self._form = None

    def decode_object(self, src_dir, uuid, dest_dir, dest_path, version, header_data):
        self.set_header_data(header_data)
        self.set_write_decode_mode(dest_dir, dest_path)
        self.decode_data(src_dir, uuid)
        self.decode_code(src_dir)

    @property
    def name(self):
        return self.header.get('name')

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
                self.code['obj'], encoding = self.read_raw_code(_code_dir, 'module')
                self.header['code_encoding_obj'] = encoding  # можно безболезненно поменять на utf-8-sig
                self.header[f'code_info_obj'] = 1
            else:
                self.decode_form0(src_dir, self.header["uuid"])
                pass

    def decode_old_elements(self):
        try:
            if not self.form[0]:
                return
            _ver = self.form[0][0][0]
            if _ver == '2':
                self.elements_tree = FormElement803.decode_list(self, self.form[0][0][1], 23)
                # self.props = FormPros802.decode_list(self, self.form[0][0][2][2])
            else:
                form = Form27(self)
                form.decode(self.form[0][0])
                # self.elements_tree, self.elements_data = Form27.decode_elements(self, self.form[0][0])
                # self.elements_tree = FormElement802.decgode_list(self, self.form[0][0][1][2][2])
                # self.props = FormProps802.decode_list(self, self.form[0][0][2][2])
        except Exception as err:
            pass  # todo если какие то елементы формы не разбираются, не прерываем
            # raise ExtException(parent=err)

    def write_decode_object(self, dest_dir, dest_path, file_name):
        super(Form8x, self).write_decode_object(dest_dir, dest_path, file_name)
        helper.json_write(self.form, self.new_dest_dir, f'{file_name}.form{self.version}.json')
        if self.elements_tree or self.props or self.params or self.commands:
            helper.json_write(
                dict(
                    tree=self.elements_tree,
                    data=self.elements_data,
                    params=self.params,
                    props=self.props,
                    commands=self.commands
                ),
                self.new_dest_dir, f'{file_name}.elements{self.version}.json')
        return []

    def decode_data(self, src_dir, uuid):
        raise NotImplemented()

    def get_decode_header(self, header):
        return self.get_decode_obj_header(header)[1][1]

    def get_decode_obj_header(self, header_data):
        return header_data[0][1] if self.obj_version == '0' else header_data[0][1][1]

    def encode_object(self, src_dir, file_name, dest_dir):
        super(Form8x, self).encode_object(src_dir, file_name, dest_dir)
        try:
            version = self.options.get('version')
            if version is None:
                version = '803' if self.header['Тип формы'] == 1 else '802'
            version = version[:3]
            self.form = helper.json_read(src_dir, f'{file_name}.form{version}.json')
        except FileNotFoundError:
            self.form = self.encode_empty_form()
        self.encode_data()
        self.encode_nested_includes(src_dir, file_name, dest_dir, None)

    def encode_old_elements(self, src_dir, file_name, dest_dir, parent_id):
        def get_form2_elem_index(_root_data, _file_name):
            try:
                index_command_panel_count = calc_offset([(21, 0)], _root_data)
                command_panel_count = int(_root_data[index_command_panel_count])
                index_root_elem_count = index_command_panel_count + command_panel_count + 1
                return index_root_elem_count, index_command_panel_count
            except Exception as err:
                raise ExtException(
                    message='случай требующий анализа, предоставьте образец формы разработчикам',
                    detail=f'{self.header["name"]} {_file_name}, {err}')

        try:
            if not self.form[0]:
                return
            _ver = self.form[0][0][0]
            if _ver == '2':
                root_data = self.form[0][0][1]
                index = get_form2_elem_index(root_data, file_name)
                index_root_element_count = index[0]
                if root_data[index_root_element_count] == 'Дочерние элементы отдельно':
                    elements = helper.json_read(src_dir, f'{file_name}.elements{self.version}.json')
                    self.elements_tree = elements['tree']
                    self.elements_data = elements['data']
                    # root_data[index_root_element_count] = str(len(self.elements_tree))
                    FormElement803.encode_list(self, self.elements_tree, root_data, index_root_element_count)
            else:
                Form27(self).encode(src_dir, file_name, self.version, self.form[0][0])
                # FormElement802.encode_list(self, src_dir, file_name, self.version, self.form[0][0][1][2][2])
                # FormProps802.encode_list(self, src_dir, file_name, self.version, self.form[0][0][2][2])
        except Exception as err:
            raise ExtException(parent=err, message='Ошибка при сборке формы', detail=f'{file_name} {src_dir}')

    def encode_header(self):
        return self.header['data']

    def encode_nested_includes(self, src_dir, file_name, dest_dir, parent_id):
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
        helper.brace_file_write(self.encode_header(), dest_dir, self.header["uuid"])
        self.file_list.append(self.header["uuid"])
        if self.header.get('code_info_obj'):
            dir_name = f'{self.header["uuid"]}.0'
            _code_dir = os.path.join(dest_dir, dir_name)
            self.file_list.append(dir_name)
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
