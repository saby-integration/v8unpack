import os
import re

from .FormElements26.FormElements26 import FormElements26
from .FormElements27.FormElements27 import FormElements27
from .FormElements4.FormElements4 import FormElements4
from v8unpack.MetaDataObject.core.Simple import SimpleNameFolder
from v8unpack import helper
from v8unpack.ext_exception import ExtException
import json

OF = '0'  # обычные формы
UF = '1'  # управляемые формы


class FormCore(SimpleNameFolder):
    _obj_name = "Form"
    double_quotes = re.compile(r'("")')
    quotes = re.compile(r'(")')
    supported_form_versions = {
        # '0-2': FormElements2,
        # '0-23': FormElements26,# 801
        # '0-25': FormElements26,# 801
        '0-26': FormElements26,  # 801
        '0-27': FormElements27,  # OF
        '1': FormElements4,  # UF
        # '1-4-50': FormElements4,
        # '1-4-49': FormElements4,
        # '1-3-49': FormElements4
    }

    def __init__(self, *, meta_obj_class=None, obj_version=None, options=None):
        super().__init__(meta_obj_class=meta_obj_class, obj_version=obj_version, options=options)
        # self.form = []
        self.elements_tree = []
        self.elements_data = {}
        self.props_index = {}
        self.props = []
        self.params = []
        self.commands = []
        self._form = None

    @property
    def form(self):
        try:
            return self.header['form']
        except KeyError:
            self.header['form'] = []
        return self.header['form']

    @form.setter
    def form(self, value):
        self.header['form'] = value

    @classmethod
    def get_form_root(cls, header_data):
        return header_data[0][1][1]

    def get_decode_header(self, header_data):
        try:
            _form_root_getter = getattr(self.meta_obj_class, 'get_form_root')
        except Exception as err:
            _form_root_getter = self.get_form_root
        return _form_root_getter(header_data)[1][1]

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        # self.decode_header(header_data)
        self.set_write_decode_mode(dest_dir, dest_path)
        self.decode_data(src_dir, file_name)

    def decode_form0(self, src_dir):
        file_name = f'{self.header["uuid"]}.0'
        _code_dir = os.path.join(src_dir, file_name)
        if os.path.exists(_code_dir):
            if os.path.isdir(_code_dir):
                self.decode_form0_from_dir(_code_dir)
            else:
                self.decode_form0_from_file(_code_dir, file_name)
                pass

    def decode_form1(self, src_dir):
        try:
            form = helper.brace_file_read(src_dir, f'{self.header["uuid"]}.1')
        except FileNotFoundError:
            return
        self.form.append(form)

    def decode_form0_from_dir(self, src_dir):
        self.form.append(helper.brace_file_read(src_dir, 'form'))
        self.code['obj'], encoding = self.read_raw_code(src_dir, 'module', uncomment_directive=True)
        self.header['code_encoding_obj'] = encoding  # можно безболезненно поменять на utf-8-sig
        self.header[f'code_info_obj'] = 1

    def decode_form0_from_file(self, src_dir, file_name=None):
        if file_name is None:
            file_name = f'{self.header["uuid"]}.0'
        try:
            form = helper.brace_file_read(src_dir, file_name)
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

    def get_form_element_decoder(self):
        self.header['Версия элементов формы'] = ''
        if not self.form or not self.form[0]:
            return
        self.header['Версия элементов формы'] = self.header['Тип формы']
        try:
            return self.supported_form_versions[self.header['Версия элементов формы']]
        except KeyError:
            pass

        self.header['Версия элементов формы'] += f"-{self.form[0][0][0]}"
        try:
            return self.supported_form_versions[self.header['Версия элементов формы']]
        except KeyError:
            pass

        try:
            v2 = self.form[0][0][1][0]
            self.header['Версия элементов формы'] += f'-{v2}'
        except (KeyError, TypeError, AttributeError):
            pass

        try:
            return self.supported_form_versions[self.header['Версия элементов формы']]
        except KeyError:
            ver = self.header['Версия элементов формы']
            return

    def decode_includes(self, src_dir, dest_dir, dest_path, header_data):
        try:
            if self.header['Тип формы'] == OF:
                self.decode_form0(src_dir)
                self.decode_code(src_dir, uncomment_directive=True)
            else:
                self.decode_form0_from_file(src_dir)
            self.decode_form1(src_dir)

            form_element_decoder = self.get_form_element_decoder()
            if not form_element_decoder:
                return

            backup = json.dumps(self.form)
            try:
                form_element_decoder(self).decode(src_dir, dest_dir, dest_path, self.form[0][0])
            except Exception as err:
                self.form = json.loads(backup)
                pass  # todo если какие то елементы формы не разбираются, не прерываем
                # raise ExtException(parent=err, message='Ошибка при разборе формы')

            #
            #
            # if self.header.get('Тип формы') == OF:
            #     self.decode_old_elements()
            #     return
        except Exception as err:
            raise ExtException(parent=err)

    def write_decode_object(self, dest_dir, dest_path, file_name):
        dest_full_path = os.path.join(dest_dir, dest_path)
        id_data = {
            'uuid': self.header.pop('uuid'),
            # 'name': self.header.pop('name'),
        }
        self.header['obj_version'] = self.obj_version
        helper.json_write(id_data, dest_full_path, f'{file_name}.id.json')
        helper.json_write(self.header, dest_full_path, f'{file_name}.json')
        self.write_decode_code(dest_full_path, file_name)

        # helper.json_write(self.form, self.new_dest_dir, f"{typed_file_name}.form.json")
        # if self.elements_tree or self.props or self.params or self.commands:
        helper.json_write(
            dict(
                params=self.params,
                props=self.props,
                commands=self.commands,
                tree=self.elements_tree,
                data=self.elements_data,
            ),
            self.new_dest_dir, f"{file_name}.elem.json")
        return []

    def decode_data(self, src_dir, uuid):
        _header_obj = self.meta_obj_class.get_form_root(self.header['header'])
        # self.header['Версия формы'] = _header_obj[1][0]
        try:
            self.header['Тип формы'] = _header_obj[1][3]
        except IndexError:
            self.header['Тип формы'] = OF
        return _header_obj

    # def get_decode_header(self, header):
    #     return self.get_decode_obj_header(header)[1][1]
    #
    # def get_decode_obj_header(self, header_data):
    #     return header_data[0][1] if self.obj_version == '0' else header_data[0][1][1]

    def encode_object(self, src_dir, file_name, dest_dir):
        super(FormCore, self).encode_object(src_dir, file_name, dest_dir)
        # try:
        # version = self.options.get('version')
        # if version is None:
        # version = '803' if str(self.header['Тип формы']) == '1' else '802'
        # version = version[:3]

        # self.form = helper.json_read(src_dir, f'{file_name}.form.json')
        # self.form = helper.json_read(src_dir, f'{file_name}.form{version}.json')
        # except FileNotFoundError:
        #     self.form = None
        # raise ExtException(message='File not found', detail=f'{src_dir} {}')
        # self.form = self.encode_empty_form()
        self.encode_data()
        self.encode_nested_includes(src_dir, file_name, dest_dir, None)

    def encode_header(self):
        try:
            form_header = self.get_decode_header(self.header['header'])
            helper.encode_header(self, form_header)
            return self.header['header']
        except Exception as err:
            raise ExtException(parent=err)

    def encode_nested_includes(self, src_dir, file_name, dest_dir, parent_id):
        # if self.header.get('Тип формы') == OF:
        #     self.encode_old_elements(src_dir, file_name, dest_dir, parent_id)
        #     return

        if not self.form or not self.form[0]:
            return

        form_element_decoder = self.get_form_element_decoder()
        if not form_element_decoder:
            return

        # try:
        #     current_form_version = f'{self.form[0][0][0]}-{self.form[0][0][1][0]}'
        #     if current_form_version not in self.supported_form_versions:
        #         return
        # except:
        #     return
        try:
            form_element_decoder(self).encode(src_dir, file_name, dest_dir, self.form[0][0])
        except Exception as err:
            raise ExtException(parent=err, message='Ошибка при сборке формы',
                               detail=f"{os.path.join(src_dir, file_name)}",
                               action='Form9of.encode_nested_includes'
                               )

    def write_encode_object(self, dest_dir):
        try:
            if self.header['Тип формы'] == OF:
                self.write_old_encode_object(dest_dir)
            else:
                helper.brace_file_write(self.encode_header(), dest_dir, self.header["uuid"])
                self.file_list.append(self.header["uuid"])
                if self.form:
                    file_name = f'{self.header["uuid"]}.0'
                    helper.brace_file_write(self.form[0], dest_dir, file_name)
                    self.file_list.append(file_name)
            if self.form and len(self.form) > 1:
                file_name = f'{self.header["uuid"]}.1'
                helper.brace_file_write(self.form[1], dest_dir, file_name)
                self.file_list.append(file_name)
        except Exception as err:
            raise ExtException(parent=err,
                               detail=f'{self.__class__.__name__} {self.header["name"]} {self.header["uuid"]}')

    def encode_data(self):
        if self.header['Тип формы'] == OF:
            return
        try:
            _code = self.code.pop('obj', "")
            _code = self.quotes.sub(r'""', _code)
            form0 = self.form[0]
            self.getset_form_code(form0, helper.str_encode(_code), self.header)
        except IndexError:
            pass
        return self.form

    def encode_empty_form(self):
        raise NotImplemented()

    def encode_write(self, dest_dir):
        raise NotImplemented()

    def write_encode_code(self, dest_dir, *, comment_directive=False):
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
            self.write_raw_code(self.code.get('obj', ''), _code_dir, 'module', encoding=_encoding,
                                comment_directive=True)

    @classmethod
    def get_last_level_array(cls, data):
        while True:
            if isinstance(data[-1], list):
                return cls.get_last_level_array(data[-1])
            else:
                return data
