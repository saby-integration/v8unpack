from .FormCore import FormCore


class Form5(FormCore):
    pass
    # @classmethod
    # def get_decode_header(cls, header_data):
    #     return header_data[0][1][1][1]

    #
    # def decode_code(self, src_dir):
    #     self.decode_old_form(src_dir)

    # def decode_data(self, src_dir, uuid):
    #     self.header['Тип формы'] = '0'
    #     pass

    # def write_encode_object(self, dest_dir):
    #     self.write_old_encode_object(dest_dir)
    #
    # def encode_data(self):
    #     pass

    # def encode_nested_includes(self, src_dir, file_name, dest_dir, parent_id):
    #     self.encode_old_elements(src_dir, file_name, dest_dir, parent_id)

    # def encode_header(self):
    #     return [[
    #         "1",
    #         [
    #             "0",
    #             [
    #                 "7",
    #                 [
    #                     self.header['h0'],
    #                     [
    #                         self.header['h1_0'],
    #                         "0",
    #                         self.header['uuid']
    #                     ],
    #                     helper.str_encode(self.header['name']),
    #                     helper.encode_name2(self.header),
    #                     helper.str_encode(self.header['comment']),
    #                 ],
    #                 "0",
    #             ]
    #         ],
    #         "0"
    #     ]]
    #
    # def encode_empty_form(self):
    #     return [[
    #         "26",
    #         [
    #             "16",
    #             [
    #                 [
    #                     "1",
    #                     "1",
    #                     [
    #                         "\"ru\"",
    #                         f"\"{self.header['name']}\""
    #                     ]
    #                 ],
    #                 "3",
    #                 "2"
    #             ],
    #             [
    #                 "09ccdc77-ea1a-4a6d-ab1c-3435eada2433",
    #                 [
    #                     "1",
    #                     [
    #                         [
    #                             "10",
    #                             "1",
    #                             [
    #                                 "3",
    #                                 "4",
    #                                 [
    #                                     "0"
    #                                 ]
    #                             ],
    #                             [
    #                                 "3",
    #                                 "4",
    #                                 [
    #                                     "0"
    #                                 ]
    #                             ],
    #                             [
    #                                 "6",
    #                                 "3",
    #                                 "0",
    #                                 "1"
    #                             ],
    #                             "0",
    #                             [
    #                                 "3",
    #                                 "3",
    #                                 [
    #                                     "-22"
    #                                 ]
    #                             ],
    #                             [
    #                                 "3",
    #                                 "4",
    #                                 [
    #                                     "0"
    #                                 ]
    #                             ],
    #                             [
    #                                 "3",
    #                                 "4",
    #                                 [
    #                                     "0"
    #                                 ]
    #                             ],
    #                             [
    #                                 "3",
    #                                 "3",
    #                                 [
    #                                     "-7"
    #                                 ]
    #                             ],
    #                             [
    #                                 "3",
    #                                 "3",
    #                                 [
    #                                     "-21"
    #                                 ]
    #                             ],
    #                             [
    #                                 "3",
    #                                 "0",
    #                                 [
    #                                     "0"
    #                                 ],
    #                                 "0",
    #                                 "0",
    #                                 "0",
    #                                 "48312c09-257f-4b29-b280-284dd89efc1e"
    #                             ],
    #                             [
    #                                 "1",
    #                                 "0"
    #                             ]
    #                         ],
    #                         "20",
    #                         "0",
    #                         "2",
    #                         [
    #                             "0",
    #                             "2",
    #                             "1"
    #                         ],
    #                         [
    #                             "0",
    #                             "3",
    #                             "1"
    #                         ],
    #                         "0",
    #                         "2",
    #                         [
    #                             "0",
    #                             "2",
    #                             "3"
    #                         ],
    #                         [
    #                             "0",
    #                             "3",
    #                             "3"
    #                         ],
    #                         "0",
    #                         "0",
    #                         [
    #                             "3",
    #                             "1",
    #                             [
    #                                 "3",
    #                                 "0",
    #                                 [
    #                                     "0"
    #                                 ],
    #                                 "\"\"",
    #                                 "-1",
    #                                 "-1",
    #                                 "1",
    #                                 "0"
    #                             ]
    #                         ],
    #                         "0",
    #                         "1",
    #                         [
    #                             "1",
    #                             "1",
    #                             [
    #                                 "3",
    #                                 [
    #                                     "1",
    #                                     "1",
    #                                     [
    #                                         "\"ru\"",
    #                                         "\"Страница1\""
    #                                     ]
    #                                 ],
    #                                 [
    #                                     "3",
    #                                     "0",
    #                                     [
    #                                         "3",
    #                                         "0",
    #                                         [
    #                                             "0"
    #                                         ],
    #                                         "\"\"",
    #                                         "-1",
    #                                         "-1",
    #                                         "1",
    #                                         "0"
    #                                     ]
    #                                 ],
    #                                 "-1",
    #                                 "1",
    #                                 "1",
    #                                 "\"Страница1\"",
    #                                 "1"
    #                             ]
    #                         ],
    #                         "1",
    #                         "1",
    #                         "0",
    #                         "4",
    #                         [
    #                             "2",
    #                             "8",
    #                             "1",
    #                             "1",
    #                             "1",
    #                             "0",
    #                             "0",
    #                             "0",
    #                             "0"
    #                         ],
    #                         [
    #                             "2",
    #                             "8",
    #                             "0",
    #                             "1",
    #                             "2",
    #                             "0",
    #                             "0",
    #                             "0",
    #                             "0"
    #                         ],
    #                         [
    #                             "2",
    #                             "392",
    #                             "1",
    #                             "1",
    #                             "3",
    #                             "0",
    #                             "0",
    #                             "8",
    #                             "0"
    #                         ],
    #                         [
    #                             "2",
    #                             "292",
    #                             "0",
    #                             "1",
    #                             "4",
    #                             "0",
    #                             "0",
    #                             "8",
    #                             "0"
    #                         ],
    #                         "0",
    #                         "4294967295",
    #                         "5",
    #                         "64"
    #                     ],
    #                     [
    #                         "0"
    #                     ]
    #                 ],
    #                 [
    #                     "2",
    #                     [
    #                         "6ff79819-710e-4145-97cd-1618da79e3e2",
    #                         "2",
    #                         [
    #                             "1",
    #                             [
    #                                 [
    #                                     "10",
    #                                     "1",
    #                                     [
    #                                         "3",
    #                                         "4",
    #                                         [
    #                                             "0"
    #                                         ]
    #                                     ],
    #                                     [
    #                                         "3",
    #                                         "4",
    #                                         [
    #                                             "0"
    #                                         ]
    #                                     ],
    #                                     [
    #                                         "6",
    #                                         "3",
    #                                         "0",
    #                                         "1"
    #                                     ],
    #                                     "0",
    #                                     [
    #                                         "3",
    #                                         "3",
    #                                         [
    #                                             "-22"
    #                                         ]
    #                                     ],
    #                                     [
    #                                         "3",
    #                                         "4",
    #                                         [
    #                                             "0"
    #                                         ]
    #                                     ],
    #                                     [
    #                                         "3",
    #                                         "4",
    #                                         [
    #                                             "0"
    #                                         ]
    #                                     ],
    #                                     [
    #                                         "3",
    #                                         "3",
    #                                         [
    #                                             "-7"
    #                                         ]
    #                                     ],
    #                                     [
    #                                         "3",
    #                                         "3",
    #                                         [
    #                                             "-21"
    #                                         ]
    #                                     ],
    #                                     [
    #                                         "3",
    #                                         "0",
    #                                         [
    #                                             "0"
    #                                         ],
    #                                         "0",
    #                                         "0",
    #                                         "0",
    #                                         "48312c09-257f-4b29-b280-284dd89efc1e"
    #                                     ],
    #                                     [
    #                                         "1",
    #                                         "0"
    #                                     ]
    #                                 ],
    #                                 "10",
    #                                 [
    #                                     "1",
    #                                     "1",
    #                                     [
    #                                         "\"ru\"",
    #                                         "\"Выполнить\""
    #                                     ]
    #                                 ],
    #                                 "1",
    #                                 "1",
    #                                 "1",
    #                                 "0",
    #                                 "0",
    #                                 [
    #                                     "3",
    #                                     "0",
    #                                     [
    #                                         "0"
    #                                     ],
    #                                     "\"\"",
    #                                     "-1",
    #                                     "-1",
    #                                     "1",
    #                                     "0"
    #                                 ],
    #                                 [
    #                                     "0",
    #                                     "0",
    #                                     "0"
    #                                 ],
    #                                 "0",
    #                                 "0"
    #                             ],
    #                             [
    #                                 "1",
    #                                 [
    #                                     "0",
    #                                     "e1692cc2-605b-4535-84dd-28440238746c",
    #                                     [
    #                                         "3",
    #                                         "\"КнопкаВыполнитьНажатие\"",
    #                                         [
    #                                             "1",
    #                                             "\"\"",
    #                                             [
    #                                                 "1",
    #                                                 "0"
    #                                             ],
    #                                             [
    #                                                 "1",
    #                                                 "0"
    #                                             ],
    #                                             [
    #                                                 "1",
    #                                                 "0"
    #                                             ],
    #                                             [
    #                                                 "3",
    #                                                 "0",
    #                                                 [
    #                                                     "0"
    #                                                 ],
    #                                                 "\"\"",
    #                                                 "-1",
    #                                                 "-1",
    #                                                 "1",
    #                                                 "0"
    #                                             ],
    #                                             [
    #                                                 "0",
    #                                                 "0",
    #                                                 "0"
    #                                             ]
    #                                         ]
    #                                     ]
    #                                 ]
    #                             ]
    #                         ],
    #                         [
    #                             "8",
    #                             "140",
    #                             "266",
    #                             "263",
    #                             "292",
    #                             "1",
    #                             [
    #                                 "0",
    #                                 [
    #                                     "2",
    #                                     "2",
    #                                     "1",
    #                                     "-26"
    #                                 ],
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ]
    #                             ],
    #                             [
    #                                 "0",
    #                                 [
    #                                     "2",
    #                                     "0",
    #                                     "1",
    #                                     "-8"
    #                                 ],
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ]
    #                             ],
    #                             [
    #                                 "0",
    #                                 [
    #                                     "2",
    #                                     "2",
    #                                     "3",
    #                                     "-123"
    #                                 ],
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ]
    #                             ],
    #                             [
    #                                 "0",
    #                                 [
    #                                     "2",
    #                                     "0",
    #                                     "3",
    #                                     "-137"
    #                                 ],
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ]
    #                             ],
    #                             [
    #                                 "0",
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ],
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ]
    #                             ],
    #                             [
    #                                 "0",
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ],
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ]
    #                             ],
    #                             "0",
    #                             "1",
    #                             [
    #                                 "0",
    #                                 "2",
    #                                 "0"
    #                             ],
    #                             "0",
    #                             "1",
    #                             [
    #                                 "0",
    #                                 "2",
    #                                 "2"
    #                             ],
    #                             "0",
    #                             "0",
    #                             "0",
    #                             "0",
    #                             "1",
    #                             "1",
    #                             "1"
    #                         ],
    #                         [
    #                             "14",
    #                             "\"Выполнить\"",
    #                             "4294967295",
    #                             "0",
    #                             "0",
    #                             "0"
    #                         ],
    #                         [
    #                             "0"
    #                         ]
    #                     ],
    #                     [
    #                         "6ff79819-710e-4145-97cd-1618da79e3e2",
    #                         "3",
    #                         [
    #                             "1",
    #                             [
    #                                 [
    #                                     "10",
    #                                     "1",
    #                                     [
    #                                         "3",
    #                                         "4",
    #                                         [
    #                                             "0"
    #                                         ]
    #                                     ],
    #                                     [
    #                                         "3",
    #                                         "4",
    #                                         [
    #                                             "0"
    #                                         ]
    #                                     ],
    #                                     [
    #                                         "6",
    #                                         "3",
    #                                         "0",
    #                                         "1"
    #                                     ],
    #                                     "0",
    #                                     [
    #                                         "3",
    #                                         "3",
    #                                         [
    #                                             "-22"
    #                                         ]
    #                                     ],
    #                                     [
    #                                         "3",
    #                                         "4",
    #                                         [
    #                                             "0"
    #                                         ]
    #                                     ],
    #                                     [
    #                                         "3",
    #                                         "4",
    #                                         [
    #                                             "0"
    #                                         ]
    #                                     ],
    #                                     [
    #                                         "3",
    #                                         "3",
    #                                         [
    #                                             "-7"
    #                                         ]
    #                                     ],
    #                                     [
    #                                         "3",
    #                                         "3",
    #                                         [
    #                                             "-21"
    #                                         ]
    #                                     ],
    #                                     [
    #                                         "3",
    #                                         "0",
    #                                         [
    #                                             "0"
    #                                         ],
    #                                         "0",
    #                                         "0",
    #                                         "0",
    #                                         "48312c09-257f-4b29-b280-284dd89efc1e"
    #                                     ],
    #                                     [
    #                                         "1",
    #                                         "0"
    #                                     ]
    #                                 ],
    #                                 "10",
    #                                 [
    #                                     "1",
    #                                     "1",
    #                                     [
    #                                         "\"ru\"",
    #                                         "\"Закрыть\""
    #                                     ]
    #                                 ],
    #                                 "1",
    #                                 "1",
    #                                 "0",
    #                                 "0",
    #                                 "0",
    #                                 [
    #                                     "3",
    #                                     "0",
    #                                     [
    #                                         "0"
    #                                     ],
    #                                     "\"\"",
    #                                     "-1",
    #                                     "-1",
    #                                     "1",
    #                                     "0"
    #                                 ],
    #                                 [
    #                                     "0",
    #                                     "0",
    #                                     "0"
    #                                 ],
    #                                 "0",
    #                                 "0"
    #                             ],
    #                             [
    #                                 "1",
    #                                 [
    #                                     "0",
    #                                     "fbe38877-b914-4fd5-8540-07dde06ba2e1",
    #                                     [
    #                                         "6",
    #                                         "4294967295",
    #                                         "00000000-0000-0000-0000-000000000000",
    #                                         "142",
    #                                         [
    #                                             "1",
    #                                             "0",
    #                                             "357c6a54-357d-425d-a2bd-22f4f6e86c87",
    #                                             "2147483647",
    #                                             "0"
    #                                         ],
    #                                         "0",
    #                                         "1"
    #                                     ]
    #                                 ]
    #                             ]
    #                         ],
    #                         [
    #                             "8",
    #                             "269",
    #                             "266",
    #                             "392",
    #                             "292",
    #                             "1",
    #                             [
    #                                 "0",
    #                                 [
    #                                     "2",
    #                                     "3",
    #                                     "1",
    #                                     "-26"
    #                                 ],
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ]
    #                             ],
    #                             [
    #                                 "0",
    #                                 [
    #                                     "2",
    #                                     "0",
    #                                     "1",
    #                                     "-8"
    #                                 ],
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ]
    #                             ],
    #                             [
    #                                 "0",
    #                                 [
    #                                     "2",
    #                                     "3",
    #                                     "3",
    #                                     "-123"
    #                                 ],
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ]
    #                             ],
    #                             [
    #                                 "0",
    #                                 [
    #                                     "2",
    #                                     "0",
    #                                     "3",
    #                                     "-8"
    #                                 ],
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ]
    #                             ],
    #                             [
    #                                 "0",
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ],
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ]
    #                             ],
    #                             [
    #                                 "0",
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ],
    #                                 [
    #                                     "2",
    #                                     "-1",
    #                                     "6",
    #                                     "0"
    #                                 ]
    #                             ],
    #                             "0",
    #                             "1",
    #                             [
    #                                 "0",
    #                                 "3",
    #                                 "0"
    #                             ],
    #                             "0",
    #                             "1",
    #                             [
    #                                 "0",
    #                                 "3",
    #                                 "2"
    #                             ],
    #                             "0",
    #                             "0",
    #                             "0",
    #                             "1",
    #                             "2",
    #                             "1",
    #                             "1"
    #                         ],
    #                         [
    #                             "14",
    #                             "\"Закрыть\"",
    #                             "4294967295",
    #                             "0",
    #                             "0",
    #                             "0"
    #                         ],
    #                         [
    #                             "0"
    #                         ]
    #                     ]
    #                 ]
    #             ],
    #             "400",
    #             "300",
    #             "1",
    #             "0",
    #             "1",
    #             "4",
    #             "4",
    #             "2"
    #         ],
    #         [
    #             [
    #                 "0"
    #             ],
    #             "1",
    #             [
    #                 "1",
    #                 [
    #                     [
    #                         "0"
    #                     ],
    #                     "0",
    #                     "1",
    #                     "\"ОбработкаОбъект\"",
    #                     [
    #                         "\"Pattern\"",
    #                         [
    #                             "\"#\"",
    #                             "066f1072-e9ba-4801-872d-205b9fba31ab"
    #                         ]
    #                     ]
    #                 ]
    #             ],
    #             [
    #                 "0"
    #             ]
    #         ],
    #         [
    #             "59d6c227-97d3-46f6-84a0-584c5a2807e1",
    #             "1",
    #             [
    #                 "2",
    #                 "0",
    #                 [
    #                     "0",
    #                     "0"
    #                 ],
    #                 [
    #                     "0"
    #                 ],
    #                 "1"
    #             ]
    #         ],
    #         [
    #             "0"
    #         ],
    #         "1",
    #         "4",
    #         "1",
    #         "0",
    #         "0",
    #         "0",
    #         [
    #             "0"
    #         ],
    #         [
    #             "0"
    #         ],
    #         [
    #             "3",
    #             "0",
    #             [
    #                 "3",
    #                 "0",
    #                 [
    #                     "0"
    #                 ],
    #                 "\"\"",
    #                 "-1",
    #                 "-1",
    #                 "1",
    #                 "0"
    #             ]
    #         ],
    #         "1",
    #         "2",
    #         "0",
    #         "0",
    #         "1"
    #     ]
    #     ]
