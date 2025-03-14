from ..MetaDataObject.core.Container import FormContainer


class Document(FormContainer):
    help_file_number = 1
    ext_code = {
        'obj': 0,
        'mgr': 2
    }

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][9][1]

