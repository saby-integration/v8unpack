from ..MetaDataObject.core.Container import Container


class DocumentJournal(Container):
    help_file_number = 0
    ext_code = {
        'obj': 0,
        'mgr': 1
    }

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][3][1]
