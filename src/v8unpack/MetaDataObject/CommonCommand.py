from ..MetaDataObject.core.Simple import Simple


class CommonCommand(Simple):
    ext_code = {'obj': 2}

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][1][2][9]
