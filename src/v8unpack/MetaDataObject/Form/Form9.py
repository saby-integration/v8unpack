import json
import os

from .FormElements4.FormElement import FormElement, FormParams, FormProps, FormCommands, calc_offset
from .FormCore import FormCore, OF

from v8unpack import helper
from v8unpack.ext_exception import ExtException


class Form9(FormCore):

    def __init__(self, *, meta_obj_class=None, obj_version=None, options=None):
        super().__init__(meta_obj_class=meta_obj_class, obj_version=obj_version, options=options)

        self.params = []
        self.commands = []

    # def decode_data(self, src_dir, uuid):
    #     _header_obj = self.meta_obj_class.get_form_root(self.header['header'])
    #     # self.header['Включать в содержание справки'] = _header_obj[1][2]
    #     self.header['Версия формы'] = _header_obj[1][0]
    #     try:
    #         self.header['Тип формы'] = _header_obj[1][3]
    #     except IndexError:
    #         self.header['Тип формы'] = OF
        # try:
        #     self.header['Расширенное представление'] = _header_obj[2]
        # except IndexError:
        #     pass
        # try:
        #     self.header['ХЗ1'] = _header_obj[1][4]
        # except IndexError:
        #     pass

    # def write_decode_object(self, dest_dir, dest_path, file_name):
    #     # if self.header['Тип формы'] == OF:
    #     #     self.obj_version = 802
    #     super().write_decode_object(dest_dir, dest_path, file_name)

        # if self.props:
        #     helper.json_write(self.props, self.new_dest_dir, f'{file_name}.props{self.options['version']}.json')
        # if self.commands:
        #     helper.json_write(self.commands, self.new_dest_dir, f'{file_name}.commands{self.options['version']}.json')
        # if self.params:
        #     helper.json_write(self.params, self.new_dest_dir, f'{file_name}.params{self.options['version']}.json')
        # if self.command_panels:
        #     helper.json_write(self.command_panels, self.new_dest_dir, f'{file_name}.panels{self.options['version']}.json')

    # def decode_code(self, src_dir):
    #     if self.header['Тип формы'] == OF:
    #         self.decode_old_form(src_dir)
    #     else:
    #         super().decode_code(src_dir)
    #     self.decode_form1(src_dir)

    # def encode_header(self):
    #     return [[
    #         "1",
    #         [
    #             "1",
    #             [
    #                 "0",
    #                 self.encode_header_title(),
    #                 self.header.get('Расширенное представление', ['0'])
    #             ]
    #         ],
    #         "0"
    #     ]]

    # def encode_header_title(self):
    #     version = self.header.get('Версия803', '13')
    #     header_title = [
    #         version,
    #         [
    #             self.header['h0'],
    #             [
    #                 self.header['h1_0'],
    #                 "0",
    #                 self.header['uuid']
    #             ],
    #             helper.str_encode(self.header['name']),
    #             helper.encode_name2(self.header),
    #             helper.str_encode(self.header['comment']),
    #             *self.header['h5'],
    #         ],
    #         self.header['Включать в содержание справки'],
    #         self.header['Тип формы']
    #     ]
    #     try:
    #         header_title.append(self.header['ХЗ1'])
    #     except KeyError:
    #         pass
    #     return header_title

    # def encode_empty_form(self):
    #     return [[
    #         "4",
    #         [
    #             "49",
    #             "0",
    #             "0",
    #             "0",
    #             "0",
    #             "1",
    #             "0",
    #             "0",
    #             "00000000-0000-0000-0000-000000000000",
    #             "1",
    #             [
    #                 "1",
    #                 "0"
    #             ],
    #             "0",
    #             "0",
    #             "1",
    #             "1",
    #             "1",
    #             "0",
    #             "1",
    #             "0",
    #             [
    #                 "0",
    #                 "1",
    #                 "0"
    #             ],
    #             [
    #                 "0"
    #             ],
    #             "1",
    #             [
    #                 "22",
    #                 [
    #                     "-1",
    #                     "02023637-7868-4a5f-8576-835a76e0c9ba"
    #                 ],
    #                 "0",
    #                 "0",
    #                 "0",
    #                 "9",
    #                 "\"\"",
    #                 [
    #                     "1",
    #                     "0"
    #                 ],
    #                 [
    #                     "1",
    #                     "0"
    #                 ],
    #                 "0",
    #                 "1",
    #                 "0",
    #                 "0",
    #                 "0",
    #                 "2",
    #                 "2",
    #                 [
    #                     "3",
    #                     "4",
    #                     [
    #                         "0"
    #                     ]
    #                 ],
    #                 [
    #                     "7",
    #                     "3",
    #                     "0",
    #                     "1",
    #                     "100"
    #                 ],
    #                 [
    #                     "0",
    #                     "0",
    #                     "0"
    #                 ],
    #                 "1",
    #                 [
    #                     "0",
    #                     "0",
    #                     "1"
    #                 ],
    #                 "0",
    #                 "1",
    #                 "0",
    #                 "0",
    #                 "0",
    #                 "3",
    #                 "3",
    #                 "0"
    #             ],
    #             "0",
    #             "\"\"",
    #             "\"\"",
    #             "1",
    #             [
    #                 "22",
    #                 [
    #                     "0"
    #                 ],
    #                 "0",
    #                 "0",
    #                 "0",
    #                 "7",
    #                 "\"Navigator\"",
    #                 [
    #                     "1",
    #                     "0"
    #                 ],
    #                 [
    #                     "1",
    #                     "0"
    #                 ],
    #                 "0",
    #                 "1",
    #                 "0",
    #                 "0",
    #                 "0",
    #                 "2",
    #                 "2",
    #                 [
    #                     "3",
    #                     "4",
    #                     [
    #                         "0"
    #                     ]
    #                 ],
    #                 [
    #                     "7",
    #                     "3",
    #                     "0",
    #                     "1",
    #                     "100"
    #                 ],
    #                 [
    #                     "0",
    #                     "0",
    #                     "0"
    #                 ],
    #                 "0",
    #                 "0",
    #                 "1",
    #                 "0",
    #                 "1",
    #                 [
    #                     "11",
    #                     [
    #                         "0"
    #                     ],
    #                     "0",
    #                     "0",
    #                     "0",
    #                     "0",
    #                     "\"NavigatorExtendedTooltip\"",
    #                     [
    #                         "1",
    #                         "0"
    #                     ],
    #                     [
    #                         "1",
    #                         "0"
    #                     ],
    #                     "1",
    #                     "0",
    #                     "0",
    #                     "2",
    #                     "2",
    #                     [
    #                         "3",
    #                         "4",
    #                         [
    #                             "0"
    #                         ]
    #                     ],
    #                     [
    #                         "7",
    #                         "3",
    #                         "0",
    #                         "1",
    #                         "100"
    #                     ],
    #                     [
    #                         "0",
    #                         "0",
    #                         "0"
    #                     ],
    #                     "1",
    #                     [
    #                         "5",
    #                         "0",
    #                         "0",
    #                         "3",
    #                         "0",
    #                         [
    #                             "0",
    #                             "1",
    #                             "0"
    #                         ],
    #                         [
    #                             "3",
    #                             "4",
    #                             [
    #                                 "0"
    #                             ]
    #                         ],
    #                         [
    #                             "3",
    #                             "4",
    #                             [
    #                                 "0"
    #                             ]
    #                         ],
    #                         [
    #                             "3",
    #                             "0",
    #                             [
    #                                 "0"
    #                             ],
    #                             "0",
    #                             "1",
    #                             "0",
    #                             "48312c09-257f-4b29-b280-284dd89efc1e"
    #                         ]
    #                     ],
    #                     "0",
    #                     "1",
    #                     "2",
    #                     [
    #                         "1",
    #                         [
    #                             "1",
    #                             "0"
    #                         ],
    #                         "0"
    #                     ],
    #                     "0",
    #                     "0",
    #                     "1",
    #                     "0",
    #                     "0",
    #                     "1",
    #                     "0",
    #                     "3",
    #                     "3",
    #                     "0"
    #                 ],
    #                 "0",
    #                 "3",
    #                 "3",
    #                 "0"
    #             ],
    #             "1",
    #             "\"\"",
    #             "0",
    #             "0",
    #             "0",
    #             "0",
    #             "0",
    #             "0",
    #             "3",
    #             "3",
    #             "0",
    #             "0",
    #             "0",
    #             "100",
    #             "1",
    #             "1",
    #             "0",
    #             "0",
    #             "0",
    #             [
    #                 "49",
    #                 "0"
    #             ]
    #         ],
    #         "Код в отдельном файле",
    #         [
    #             "4",
    #             "1",
    #             [
    #                 "9",
    #                 [
    #                     "1"
    #                 ],
    #                 "0",
    #                 "\"Объект\"",
    #                 [
    #                     "1",
    #                     "0"
    #                 ],
    #                 [
    #                     "\"Pattern\"",
    #                     [
    #                         "\"#\"",
    #                         "7cadabb8-6ade-4026-bc22-5e7e789b0b4b"
    #                     ]
    #                 ],
    #                 [
    #                     "0",
    #                     [
    #                         "0",
    #                         [
    #                             "\"B\"",
    #                             "1"
    #                         ],
    #                         "0"
    #                     ]
    #                 ],
    #                 [
    #                     "0",
    #                     [
    #                         "0",
    #                         [
    #                             "\"B\"",
    #                             "1"
    #                         ],
    #                         "0"
    #                     ]
    #                 ],
    #                 [
    #                     "0",
    #                     "0"
    #                 ],
    #                 [
    #                     "0",
    #                     "0"
    #                 ],
    #                 "1",
    #                 "0",
    #                 "0",
    #                 "0",
    #                 [
    #                     "0",
    #                     "0"
    #                 ],
    #                 [
    #                     "0",
    #                     "0"
    #                 ]
    #             ],
    #             "0",
    #             "0",
    #             [
    #                 "#base64:77u/PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4NCjxTZXR0aW5ncyB4bWxucz0iaHR0cDovL3Y4LjFjLnJ1LzguMS9kYXRhLWNvbXBvc2l0aW9uLXN5c3RlbS9zZXR0aW5ncyIgeG1sbnM6ZGNzY29yPSJodHRwOi8vdjguMWMucnUvOC4xL2RhdGEtY29tcG9zaXRpb24tc3lzdGVtL2NvcmUiIHhtbG5zOnN0eWxlPSJodHRwOi8vdjguMWMucnUvOC4xL2RhdGEvdWkvc3R5bGUiIHhtbG5zOnN5cz0iaHR0cDovL3Y4LjFjLnJ1LzguMS9kYXRhL3VpL2ZvbnRzL3N5c3RlbSIgeG1sbnM6djg9Imh0dHA6Ly92OC4xYy5ydS84LjEvZGF0YS9jb3JlIiB4bWxuczp2OHVpPSJodHRwOi8vdjguMWMucnUvOC4xL2RhdGEvdWkiIHhtbG5zOndlYj0iaHR0cDovL3Y4LjFjLnJ1LzguMS9kYXRhL3VpL2NvbG9ycy93ZWIiIHhtbG5zOndpbj0iaHR0cDovL3Y4LjFjLnJ1LzguMS9kYXRhL3VpL2NvbG9ycy93aW5kb3dzIiB4bWxuczp4cz0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEiIHhtbG5zOnhzaT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEtaW5zdGFuY2UiPg0KCTxvdXRwdXRQYXJhbWV0ZXJzLz4NCjwvU2V0dGluZ3M+"
    #             ]
    #         ],
    #         [
    #             "0",
    #             "0"
    #         ],
    #         [
    #             "0",
    #             "0"
    #         ],
    #         [
    #             "0",
    #             "0"
    #         ],
    #         [
    #             "0",
    #             "0"
    #         ],
    #         "0",
    #         "0"
    #     ]]
