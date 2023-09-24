from ..MetaDataObject.core.Container import Container
from .. import helper


class ChartOfAccounts(Container):
    ext_code = {
        'obj': 14,
        # 'mgr': хз
    }
    help_file_number = 5
    predefined_file_number = 9

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][15][1]
