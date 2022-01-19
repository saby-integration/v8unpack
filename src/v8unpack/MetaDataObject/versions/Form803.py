import re

from .Form8x import Form8x
from ... import helper
from ...ext_exception import ExtException

OLD_FORM = '0'
UPR_FORM = '1'


class Form803(Form8x):
    ver = '803'
    double_quotes = re.compile('("")')
    quotes = re.compile('(")')

    def decode_data(self, src_dir, uuid):
        _header_obj = self.get_decode_obj_header(self.header['data'])
        self.header['Включать в содержание справки'] = _header_obj[1][2]
        self.header['Тип формы'] = _header_obj[1][3]
        self.header['Версия803'] = _header_obj[1][0]

        try:
            self.header['Расширенное представление'] = _header_obj[2]
        except IndexError:
            pass

        if self.header['Тип формы'] != OLD_FORM:
            self.decode_form0(src_dir, uuid)

    def decode_form0(self, src_dir, uuid):
        try:
            form = helper.json_read(src_dir, f'{uuid}.0.json')
        except FileNotFoundError:
            return
        try:
            _code = helper.str_decode(self.getset_form_code(form, 'Код в отдельном файле', self.header))
            if _code:
                _code = self.double_quotes.sub('"', _code)
                self.code['obj'] = _code
                self.header['code_info_obj'] = 'Код в отдельном файле'
        except Exception as err:
            raise ExtException(parent=err, detail=self.header['uuid'])
        self.form.append(form)

    @classmethod
    def get_last_level_array(cls, data):
        while True:
            if isinstance(data[-1], list):
                return cls.get_last_level_array(data[-1])
            else:
                return data

    @classmethod
    def getset_form_code(cls, form, new_value=None, header=None):
        err_detail = f'{header["uuid"]} {header["name"]} ' \
                     f'опытным путем подобрано, если у Вас код не где то не достается' \
                     f'обновитесь до последней версии, и если не поможет создайте issue с дампом'
        len_form_0 = len(form[0])
        if len_form_0 > 2 and form[0][0] in ['4', '3']:
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

    def decode_form1(self, src_dir, uuid):
        try:
            form = helper.json_read(src_dir, f'{uuid}.1.json')
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
        return [
            self.header.get('Версия803', '13'),
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
            self.header['Тип формы'],
            [
                "2",
                [
                    "\"#\"",
                    "1708fdaa-cbce-4289-b373-07a5a74bee91",
                    "1"
                ],
                [
                    "\"#\"",
                    "1708fdaa-cbce-4289-b373-07a5a74bee91",
                    "2"
                ]
            ]
        ]

    def encode_data(self):
        if self.header['Тип формы'] == OLD_FORM:
            return
        try:
            _code = self.code.pop('obj', "")
            _code = self.quotes.sub('""', _code)
            form0 = self.form[0]
            self.getset_form_code(form0, helper.str_encode(_code), self.header)
        except IndexError:
            pass
        return self.form

    def write_encode_object(self, dest_dir):
        if self.header['Тип формы'] == OLD_FORM:
            self.write_old_encode_object(dest_dir)
        else:
            helper.json_write(self.encode_header(), dest_dir, f'{self.header["uuid"]}.json')
            if self.form:
                helper.json_write(self.form[0], dest_dir, f'{self.header["uuid"]}.0.json')
        if self.form and len(self.form) > 1:
            helper.json_write(self.form[1], dest_dir, f'{self.header["uuid"]}.1.json')

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
