from ..MetaDataObject.core.Container import Container


class Document(Container):
    help_file_number = 1
    ext_code = {
        'obj': 0,
        'mgr': 2
    }

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][9][1]
