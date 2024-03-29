from ..MetaDataObject.core.Container import Container


class ChartOfCalculationTypes(Container):
    ext_code = {
        'obj': 0,
        'mgr': 3
    }
    help_file_number = 1
    predefined_file_number = 2

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][1][1]
