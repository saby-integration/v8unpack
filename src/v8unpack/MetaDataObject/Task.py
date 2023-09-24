from ..MetaDataObject.core.Container import Container


class Task(Container):
    ext_code = {
        'obj': 6,
        'mgr': 7
    }
    help_file_number = 5
    # @classmethod
    # def get_decode_header(cls, header):
    #     return header[0][1][9][1]
