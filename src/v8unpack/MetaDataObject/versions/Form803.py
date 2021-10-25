import re

from .Form8x import Form8x
from ... import helper


class Form803(Form8x):
    ver = '803'
    double_quotes = re.compile('("")')
    quotes = re.compile('(")')

    def decode_data(self, src_dir, uuid):
        self.form = helper.json_read(src_dir, f'{uuid}.0.json')
        try:
            _code = helper.str_decode(self.form[0][2])
            if _code:
                _code = self.double_quotes.sub('"', _code)
                self.code['obj'] = _code
                self.header['code_info_obj'] = 'Код в отдельном файле'
                self.form[0][2] = 'Код в отдельном файле'
        except IndexError:
            pass  # todo код расширения не достается

        try:
            _header_obj = self.get_decode_obj_header(self.header['data'])
            self.header['Включать в содержание справки'] = _header_obj[1][2]
            self.header['Расширенное представление'] = _header_obj[2]
        except IndexError:
            pass

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
            "13",
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
            "1",
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
        try:
            _code = self.code.pop('obj', "")
            _code = self.quotes.sub('""', _code)
            self.form[0][2] = helper.str_encode(_code)
        except IndexError:
            pass
        return self.form

    def write_encode_object(self, dest_dir):
        helper.json_write(self.encode_header(), dest_dir, f'{self.header["uuid"]}.json')
        helper.json_write(self.form, dest_dir, f'{self.header["uuid"]}.0.json')

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
