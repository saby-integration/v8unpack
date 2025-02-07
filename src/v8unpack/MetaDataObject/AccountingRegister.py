from ..MetaDataObject.core.Container import Container


class AccountingRegister(Container):
    ext_code = {
        'obj': 6,
        'mgr': 7
    }
    help_file_number = 5

    @classmethod
    def get_decode_header(cls, header):
        obj_version = int(header[0][1][0])
        if obj_version > 21:
            return header[0][1][16][1]
        else:
            return header[0][1][15][1]
