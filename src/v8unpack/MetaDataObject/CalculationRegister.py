from ..MetaDataObject.core.Container import Container


class CalculationRegister(Container):
    ext_code = {
        'obj': 1,
        # 'mgr': хз
    }
    help_file_number = 0

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][15][1]
