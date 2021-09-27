from .Form83 import Form83


class DocumentForm83(Form83):
    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][1][1]

    def encode_header(self):
        return [[
            "1",
            [
                "0",
                self.encode_header_title(),
            ],
            "0"
        ]]
