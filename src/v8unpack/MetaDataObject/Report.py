from ..MetaDataObject.core.Container import Container


class Report(Container):
    ext_code = {
        'mgr': '2',  # модуль менеджера Отчета
        'obj': '0',  # модуль Отчета
    }

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][3][1]
