from ..MetaDataObject.core.SimpleWithInfo import SimpleWithInfo


class WSReference(SimpleWithInfo):
    pass

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][2]
