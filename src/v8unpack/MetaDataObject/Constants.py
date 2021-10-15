#from ..MetaDataObject.core.SimpleWithInfo import SimpleWithInfo
from ..MetaDataObject.core.Simple import Simple


class Constants(Simple):
    ext_code = {'obj': 0}  # модуль объекта Константа

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][1][1][1]

