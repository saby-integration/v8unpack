from ..MetaDataObject.core.Container import Container


class Catalog(Container):
    ext_code = {
        'mgr': '3',  # модуль менеджера Справочника
        'obj': '0',  # модуль объекта Справочника
        'pre': '1c',  # предопределенные элементы Справочника
    }

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][9][1]
