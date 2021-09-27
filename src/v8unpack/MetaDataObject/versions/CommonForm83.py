from .Form83 import Form83


class CommonForm83(Form83):
    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][1][1]

    def encode_header(self):
        return [[
            "1",
            [
                "4",
                self.encode_header_title(),
                [
                    "0"
                ],
                [
                    "0"
                ],
                "0"
            ],
            "0"
        ]]
