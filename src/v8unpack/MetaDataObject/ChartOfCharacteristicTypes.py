from ..MetaDataObject.core.Simple import Simple


class ChartOfCharacteristicTypes(Simple):
    ext_code = {
        'mgr': '16',  # модуль менеджера Плана видов характеристик
        'obj': '15',  # модуль менеджера Плана видов характеристик
        'pre': '7',  # предопределенные Плана видов характеристик
    }

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][13][1]
