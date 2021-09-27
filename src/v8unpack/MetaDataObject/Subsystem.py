from ..MetaDataObject.core.Simple import Simple


class Subsystem(Simple):
    pass

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][1]
