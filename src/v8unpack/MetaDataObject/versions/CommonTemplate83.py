from .Template83 import Template83


class CommonTemplate83(Template83):
    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][1]

    @classmethod
    def get_template_type(cls, header_data):
        return header_data[0][0]
