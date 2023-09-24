from ..MetaDataObject.core.IncludeSimple import IncludeSimple


class InformationRegisterCommand(IncludeSimple):
    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][2][9]
