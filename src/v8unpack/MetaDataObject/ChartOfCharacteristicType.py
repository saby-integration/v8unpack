from ..MetaDataObject.core.Container import Container


class ChartOfCharacteristicType(Container):
    ext_code = {
        'mgr': '16',  # модуль менеджера Плана видов характеристик
        'obj': '15',  # модуль менеджера Плана видов характеристик
    }
    help_file_number = 5
    predefined_file_number = 7

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][13][1]
