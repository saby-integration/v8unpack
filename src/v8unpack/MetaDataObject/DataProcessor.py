from ..MetaDataObject.core.Container import Container


class DataProcessor(Container):
    ext_code = {
        'mgr': '2',  # модуль менеджера
        'obj': '0',  # модуль объекта
    }
    help_file_number = 1

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][3][1]

    def encode_header(self):
        super().encode_header()
        self.set_product_comment(self.options.get('product_version'))
