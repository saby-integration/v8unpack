from ..MetaDataObject.core.Simple import Simple


class Constants(Simple):
    ext_code = {
        'mgr': '1',  # модуль менеджера Константы
        'obj': '0',  # модуль менеджера значения Константы
    }

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][1][1][1]
