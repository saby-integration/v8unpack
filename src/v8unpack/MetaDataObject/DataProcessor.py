from ..MetaDataObject.core.Container import Container


class DataProcessor(Container):
    version = '83'

    def __init__(self):
        super(DataProcessor, self).__init__()
        self.code = None

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][3][1]

    @classmethod
    def get_decode_includes(cls, header_data):
        return [header_data[0]]
