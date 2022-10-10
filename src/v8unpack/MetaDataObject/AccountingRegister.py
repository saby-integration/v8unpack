from ..MetaDataObject.core.Container import Container


class AccountingRegister(Container):
    ext_code = {
        'obj': 6,
        # 'mgr': хз
    }
    help_file_number = 5

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][15][1]
