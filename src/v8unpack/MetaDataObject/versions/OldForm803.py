from .Form801 import Form801
from .Form802 import Form802
from .Form803 import Form803


class OldForm803(Form803):
    def get_decode_obj_header(self, header):
        return header[0]

    def encode_header(self):
        return [[
            "1",
            self.encode_header_title(),
            "0"
        ]]


class OldForm802(Form802):
    def get_decode_obj_header(self, header):
        return header[0]

    def encode_header(self):
        return [[
            "1",
            self.encode_header_title(),
            "0"
        ]]


class OldForm801(Form801):
    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][1]

    # def get_decode_obj_header(self, header):
    #     return header[0]

    def encode_header(self):
        return [[
            "1",
            self.encode_header_title(),
            "0"
        ]]
