from ..MetaDataObject.core.Container import Container


class Report(Container):
    ext_code = {
        'mgr': '2',
        'obj': '0',
    }

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][3][1]
