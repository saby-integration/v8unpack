from ..MetaDataObject.core.Container import FormContainer
import os

from .. import helper
from ..MetaObject import MetaObject
from ..ext_exception import ExtException


class DataProcessor(FormContainer):
    ext_code = {
        'mgr': '2',  # модуль менеджера
        'obj': '0',  # модуль объекта
    }
    help_file_number = 1

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][3][1]

    def decode_ids(self):
        data_id = super().decode_ids()

        if self.obj_version.startswith('803'):
            manager_data = self.header['header'][0][1]
            data_id['manager_uuid1'] = manager_data[1]
            data_id['manager_uuid2'] = manager_data[2]
            data_id['manager_uuid3'] = manager_data[7]
            data_id['manager_uuid4'] = manager_data[8]
            manager_data[1] = 'manager_uuid1 в файле id'
            manager_data[2] = 'manager_uuid2 в файле id'
            manager_data[7] = 'manager_uuid3 в файле id'
            manager_data[8] = 'manager_uuid4 в файле id'

        return data_id

    def encode_ids(self, data_id):
        super().encode_ids(data_id)
        if self.obj_version.startswith('803'):
            manager_data = self.header['header'][0][1]
            manager_data[1] = data_id['manager_uuid1']
            manager_data[2] = data_id['manager_uuid2']
            manager_data[7] = data_id['manager_uuid3']
            manager_data[8] = data_id['manager_uuid4']

    def encode_header(self):
        super().encode_header()
        self.set_product_comment(self.options.get('product_version'))
