from ..MetaDataObject.core.Container import Container


class AccumulationRegister(Container):
    ext_code = {
        'mgr': '2',  # модуль менеджера
        'obj': '1',  # Модуль набора записей
    }

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][13][1]
