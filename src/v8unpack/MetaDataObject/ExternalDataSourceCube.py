from ..MetaDataObject.core.Container import Container


class ExternalDataSourceCube(Container):
    ext_code = {'obj': 2, 'mgr': 1}

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][1][1]
