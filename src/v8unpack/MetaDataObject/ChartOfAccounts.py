from ..MetaDataObject.core.Container import Container
from .. import helper


class ChartOfAccounts(Container):
    ext_code = {
        'obj': 14,
        'mgr': 15
    }
    help_file_number = 5
    predefined_file_number = 9

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][15][1]

    # @classmethod
    # def get_decode_includes(cls, header_data):
    #     return super().get_decode_includes(header_data)