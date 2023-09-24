from .Template8x import Template8x
from ... import helper


class Template802(Template8x):
    def encode_header(self):
        return [[
            "1",
            [
                "2",
                self.tmpl_type.value,
                [
                    self.header['h0'],
                    [
                        self.header['h1_0'],
                        "0",
                        self.header['uuid']
                    ],
                    helper.str_encode(self.header['name']),
                    helper.encode_name2(self.header),
                    helper.str_encode(self.header['comment'])
                ]
            ],
            "0"
        ]]
