from ..MetaDataObject.core.Container import Container
import os


class Documents(Container):
    pass

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][9][1]

    @classmethod
    def get_decode_includes(cls, header_data):
        return [header_data[0]]
