import os
import sys
import unittest

sys.path.append("../../src/")
from v8unpack import helper
from v8unpack.MetaDataObject.versions.Form803 import Form803 as Form
from v8unpack.MetaDataObject.CatalogForm import CatalogForm
from v8unpack.unittest_helper import compare_file, NotEqualLine


class TestDecodeBraceFile(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data', 'form')
        self.temp_dir = os.path.join(self.data_dir, 'temp')
        self.temp_dir2 = os.path.join(self.data_dir, 'temp2')

    def test_decode_all_raw_data(self):
        test_files = os.listdir(self.data_dir)
        result = ''
        for file_name in test_files:
            if file_name == 'temp':
                continue
            uuid, x = file_name.split('.')
            result += self.decode_raw_data(uuid)
        self.assertEqual('', result)

    def test_decode_file(self):
        uuid = '01f67911-4ca7-4668-b970-62c299b98e56'
        result = self.decode_raw_data(uuid)
        self.assertEqual('', result)

    def decode_raw_data(self, file_name):
        helper.clear_dir(self.temp_dir)
        helper.clear_dir(self.temp_dir2)
        options = dict(version='803')
        # helper.clear_dir(self.temp_dir2)
        CatalogForm.decode(self.data_dir, file_name, self.temp_dir, '', options=options)
        temp_dir = os.path.join(self.temp_dir, 'ФормаСписка')
        form = Form(options=options)
        form.encode(temp_dir, file_name, self.temp_dir2, None, [{}])
        problems = ''
        try:
            result = compare_file(
                os.path.join(self.data_dir, file_name),
                os.path.join(self.temp_dir2, file_name),
                problems
            )
        except NotEqualLine as err:
            result = err
        return result

    def test_decode_by_scheme(self):
        from v8unpack.MetaDataObject.schemes.Form import Form

        file_name = '9c80a4da-8f1f-48ae-915c-4227fef8f364'
        data = Form(self.data_dir, file_name).decode()
