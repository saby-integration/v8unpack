from ..MetaDataObject.core.Container import Container


class Documents(Container):
    pass

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][9][1]
