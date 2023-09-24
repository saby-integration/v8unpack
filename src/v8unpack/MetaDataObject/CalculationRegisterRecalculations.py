from ..MetaDataObject.core.Container import Container


class CalculationRegisterRecalculations(Container):
    pass

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][7][1]
