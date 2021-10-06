from ..MetaDataObject.core.Simple import Simple


class InformationRegister(Simple):
    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][15][1]
