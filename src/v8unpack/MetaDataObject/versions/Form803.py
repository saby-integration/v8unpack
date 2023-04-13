
import json

from .Form803Elements.FormElement import FormElement, FormParams, FormProps, FormCommands, calc_offset
from .Form8x import Form8x
from ... import helper
from ...ext_exception import ExtException

OLD_FORM = '0'
UPR_FORM = '1'


class Form803(Form8x):
    ver = '803'

    def __init__(self):
        super().__init__()
        self.command_panels = []
        self.params = []
        self.commands = []

    def decode_data(self, src_dir, uuid):
        _header_obj = self.get_decode_obj_header(self.header['data'])
        self.header['Включать в содержание справки'] = _header_obj[1][2]
        self.header['Тип формы'] = _header_obj[1][3]
        self.header['Версия803'] = _header_obj[1][0]

        try:
            self.header['Расширенное представление'] = _header_obj[2]
        except IndexError:
            pass
        try:
            self.header['ХЗ1'] = _header_obj[1][4]
        except IndexError:
            pass

        if self.header['Тип формы'] != OLD_FORM:
            self.decode_form0(src_dir, uuid)

    def decode_includes(self, src_dir, dest_dir, dest_path, header_data):
        if not self.form or not self.form[0]:
            return
        try:
            supported_form = ['4-49', '3-49']  # not supported 27-18, контур вероятно обычные формы
            current_form = f'{self.form[0][0][0]}-{self.form[0][0][1][0]}'
            if current_form not in supported_form:
                return
        except:
            return

        try:
            self.decode_elements(src_dir, dest_dir, dest_path, header_data)
            self.params = FormParams.decode_list(self, self.form[0][0])
            self.commands = FormCommands.decode_list(self, self.form[0][0])
            self.props = FormProps.decode_list(self, self.form[0][0])
        except Exception as err:
            pass  # todo если какие то елементы формы не разбираются, не прерываем
            # raise ExtException(parent=err, message='Ошибка при разборе формы')

    def decode_elements(self, src_dir, dest_dir, dest_path, header_data):
        backup = json.dumps(self.form)
        try:
            index = self.get_form_elem_index()
            root_data = self.form[0][0][1]

            # index_panel_count = index[1]
            # form_panels_count = int(root_data[index_panel_count])
            # if form_panels_count:
            #     self.command_panels = [root_data[index_panel_count + 1]]
            #     root_data[index_panel_count] = 'В отдельном файле'
            #     del root_data[index_panel_count + 1]

            index_root_element_count = index[0]
            form_items_count = int(root_data[index_root_element_count])
            if form_items_count:
                self.elements = FormElement.decode_list(self, root_data, index_root_element_count)
            pass
        except helper.FuckingBrackets as err:
            self.form = json.loads(backup)
        except Exception as err:
            raise ExtException(parent=err, message='Ошибка при разборе формы', detail=f'{dest_path}')

    def get_form_elem_index(self):
        try:
            root_data = self.form[0][0][1]
            index_command_panel_count = calc_offset([(18, 2), (3, 0)], root_data)
            command_panel_count = int(root_data[index_command_panel_count])
            index_root_elem_count = index_command_panel_count + command_panel_count + 1
            return index_root_elem_count, index_command_panel_count
        except Exception as err:
            raise ExtException(
                message='случай требующий анализа, предоставьте образец формы разработчикам',
                detail=f'{self.header["name"]}, {err}')

    def write_decode_object(self, dest_dir, dest_path, file_name, version):
        super().write_decode_object(dest_dir, dest_path, file_name, version)
        if self.commands:
            helper.json_write(self.commands, self.new_dest_dir, f'{file_name}.commands{self.ver}.json')
        if self.params:
            helper.json_write(self.params, self.new_dest_dir, f'{file_name}.params{self.ver}.json')
        if self.command_panels:
            helper.json_write(self.command_panels, self.new_dest_dir, f'{file_name}.panels{self.ver}.json')

    def decode_form1(self, src_dir, uuid):
        try:
            form = helper.brace_file_read(src_dir, f'{uuid}.1')
        except FileNotFoundError:
            return
        self.form.append(form)

    def decode_code(self, src_dir):
        if self.header['Тип формы'] == OLD_FORM:
            self.decode_old_form(src_dir)
        else:
            super().decode_code(src_dir)
        self.decode_form1(src_dir, self.header['uuid'])

    def encode_header(self):
        return [[
            "1",
            [
                "1",
                [
                    "0",
                    self.encode_header_title(),
                    self.header.get('Расширенное представление', ['0'])
                ]
            ],
            "0"
        ]]

    def encode_header_title(self):
        version = self.header.get('Версия803', '13')
        header_title = [
            version,
            [
                self.header['h0'],
                [
                    self.header['h1_0'],
                    "0",
                    self.header['uuid']
                ],
                helper.str_encode(self.header['name']),
                helper.encode_name2(self.header),
                helper.str_encode(self.header['comment']),
                *self.header['h5'],
            ],
            self.header['Включать в содержание справки'],
            self.header['Тип формы']
        ]
        try:
            header_title.append(self.header['ХЗ1'])
        except KeyError:
            pass
        return header_title

    def encode_data(self):
        if self.header['Тип формы'] == OLD_FORM:
            return
        try:
            _code = self.code.pop('obj', "")
            _code = self.quotes.sub(r'""', _code)
            form0 = self.form[0]
            self.getset_form_code(form0, helper.str_encode(_code), self.header)
        except IndexError:
            pass
        return self.form

    def encode_nested_includes(self, src_dir, file_name, dest_dir, version, parent_id):
        if not self.form or not self.form[0]:
            return
        try:
            supported_form = ['4-49', '3-49']
            if f'{self.form[0][0][0]}-{self.form[0][0][1][0]}' not in supported_form:
                return
        except:
            return
        try:
            self.encode_elements(src_dir, file_name, dest_dir, version)
            FormParams.encode_list(self, src_dir, file_name, version)
            FormCommands.encode_list(self, src_dir, file_name, version)
            FormProps.encode_list(self, src_dir, file_name, version)
        except Exception as err:
            raise ExtException(parent=err, message='Ошибка при разборе формы')

    def encode_elements(self, src_dir, file_name, dest_dir, version):
        index = self.get_form_elem_index()
        root_data = self.form[0][0][1]

        # index_panel_count = index[1]
        # form_panels_count = int(root_data[index_panel_count])
        # if form_panels_count == 'В отдельном файле':
        #     self.command_panels = helper.json_read(src_dir, f'{file_name}.panels{version}.json')

        index_root_element_count = index[0]
        if root_data[index_root_element_count] == 'Дочерние элементы отдельно':
            self.elements = helper.json_read(src_dir, f'{file_name}.elements{version}.json')
            # root_data[index_root_element_count] = str(len(self.elements))
            FormElement.encode_list(self, self.elements, root_data, index_root_element_count)

    def write_encode_object(self, dest_dir):
        if self.header['Тип формы'] == OLD_FORM:
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

    def encode_empty_form(self):
        return [[
            "4",
            [
                "49",
                "0",
                "0",
                "0",
                "0",
                "1",
                "0",
                "0",
                "00000000-0000-0000-0000-000000000000",
                "1",
                [
                    "1",
                    "0"
                ],
                "0",
                "0",
                "1",
                "1",
                "1",
                "0",
                "1",
                "0",
                [
                    "0",
                    "1",
                    "0"
                ],
                [
                    "0"
                ],
                "1",
                [
                    "22",
                    [
                        "-1",
                        "02023637-7868-4a5f-8576-835a76e0c9ba"
                    ],
                    "0",
                    "0",
                    "0",
                    "9",
                    "\"\"",
                    [
                        "1",
                        "0"
                    ],
                    [
                        "1",
                        "0"
                    ],
                    "0",
                    "1",
                    "0",
                    "0",
                    "0",
                    "2",
                    "2",
                    [
                        "3",
                        "4",
                        [
                            "0"
                        ]
                    ],
                    [
                        "7",
                        "3",
                        "0",
                        "1",
                        "100"
                    ],
                    [
                        "0",
                        "0",
                        "0"
                    ],
                    "1",
                    [
                        "0",
                        "0",
                        "1"
                    ],
                    "0",
                    "1",
                    "0",
                    "0",
                    "0",
                    "3",
                    "3",
                    "0"
                ],
                "0",
                "\"\"",
                "\"\"",
                "1",
                [
                    "22",
                    [
                        "0"
                    ],
                    "0",
                    "0",
                    "0",
                    "7",
                    "\"Navigator\"",
                    [
                        "1",
                        "0"
                    ],
                    [
                        "1",
                        "0"
                    ],
                    "0",
                    "1",
                    "0",
                    "0",
                    "0",
                    "2",
                    "2",
                    [
                        "3",
                        "4",
                        [
                            "0"
                        ]
                    ],
                    [
                        "7",
                        "3",
                        "0",
                        "1",
                        "100"
                    ],
                    [
                        "0",
                        "0",
                        "0"
                    ],
                    "0",
                    "0",
                    "1",
                    "0",
                    "1",
                    [
                        "11",
                        [
                            "0"
                        ],
                        "0",
                        "0",
                        "0",
                        "0",
                        "\"NavigatorExtendedTooltip\"",
                        [
                            "1",
                            "0"
                        ],
                        [
                            "1",
                            "0"
                        ],
                        "1",
                        "0",
                        "0",
                        "2",
                        "2",
                        [
                            "3",
                            "4",
                            [
                                "0"
                            ]
                        ],
                        [
                            "7",
                            "3",
                            "0",
                            "1",
                            "100"
                        ],
                        [
                            "0",
                            "0",
                            "0"
                        ],
                        "1",
                        [
                            "5",
                            "0",
                            "0",
                            "3",
                            "0",
                            [
                                "0",
                                "1",
                                "0"
                            ],
                            [
                                "3",
                                "4",
                                [
                                    "0"
                                ]
                            ],
                            [
                                "3",
                                "4",
                                [
                                    "0"
                                ]
                            ],
                            [
                                "3",
                                "0",
                                [
                                    "0"
                                ],
                                "0",
                                "1",
                                "0",
                                "48312c09-257f-4b29-b280-284dd89efc1e"
                            ]
                        ],
                        "0",
                        "1",
                        "2",
                        [
                            "1",
                            [
                                "1",
                                "0"
                            ],
                            "0"
                        ],
                        "0",
                        "0",
                        "1",
                        "0",
                        "0",
                        "1",
                        "0",
                        "3",
                        "3",
                        "0"
                    ],
                    "0",
                    "3",
                    "3",
                    "0"
                ],
                "1",
                "\"\"",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "3",
                "3",
                "0",
                "0",
                "0",
                "100",
                "1",
                "1",
                "0",
                "0",
                "0",
                [
                    "49",
                    "0"
                ]
            ],
            "Код в отдельном файле",
            [
                "4",
                "1",
                [
                    "9",
                    [
                        "1"
                    ],
                    "0",
                    "\"Объект\"",
                    [
                        "1",
                        "0"
                    ],
                    [
                        "\"Pattern\"",
                        [
                            "\"#\"",
                            "7cadabb8-6ade-4026-bc22-5e7e789b0b4b"
                        ]
                    ],
                    [
                        "0",
                        [
                            "0",
                            [
                                "\"B\"",
                                "1"
                            ],
                            "0"
                        ]
                    ],
                    [
                        "0",
                        [
                            "0",
                            [
                                "\"B\"",
                                "1"
                            ],
                            "0"
                        ]
                    ],
                    [
                        "0",
                        "0"
                    ],
                    [
                        "0",
                        "0"
                    ],
                    "1",
                    "0",
                    "0",
                    "0",
                    [
                        "0",
                        "0"
                    ],
                    [
                        "0",
                        "0"
                    ]
                ],
                "0",
                "0",
                [
                    "#base64:77u/PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4NCjxTZXR0aW5ncyB4bWxucz0iaHR0cDovL3Y4LjFjLnJ1LzguMS9kYXRhLWNvbXBvc2l0aW9uLXN5c3RlbS9zZXR0aW5ncyIgeG1sbnM6ZGNzY29yPSJodHRwOi8vdjguMWMucnUvOC4xL2RhdGEtY29tcG9zaXRpb24tc3lzdGVtL2NvcmUiIHhtbG5zOnN0eWxlPSJodHRwOi8vdjguMWMucnUvOC4xL2RhdGEvdWkvc3R5bGUiIHhtbG5zOnN5cz0iaHR0cDovL3Y4LjFjLnJ1LzguMS9kYXRhL3VpL2ZvbnRzL3N5c3RlbSIgeG1sbnM6djg9Imh0dHA6Ly92OC4xYy5ydS84LjEvZGF0YS9jb3JlIiB4bWxuczp2OHVpPSJodHRwOi8vdjguMWMucnUvOC4xL2RhdGEvdWkiIHhtbG5zOndlYj0iaHR0cDovL3Y4LjFjLnJ1LzguMS9kYXRhL3VpL2NvbG9ycy93ZWIiIHhtbG5zOndpbj0iaHR0cDovL3Y4LjFjLnJ1LzguMS9kYXRhL3VpL2NvbG9ycy93aW5kb3dzIiB4bWxuczp4cz0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEiIHhtbG5zOnhzaT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEtaW5zdGFuY2UiPg0KCTxvdXRwdXRQYXJhbWV0ZXJzLz4NCjwvU2V0dGluZ3M+"
                ]
            ],
            [
                "0",
                "0"
            ],
            [
                "0",
                "0"
            ],
            [
                "0",
                "0"
            ],
            [
                "0",
                "0"
            ],
            "0",
            "0"
        ]]
