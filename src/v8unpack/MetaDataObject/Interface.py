from ..MetaDataObject.core.SimpleWithInfo import SimpleWithInfo


class Interface(SimpleWithInfo):
    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][2]
