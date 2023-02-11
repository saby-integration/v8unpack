import os
import sys
import unittest

sys.path.append("../../src/")
from v8unpack import helper
from v8unpack.MetaDataObject.Form import Form
from v8unpack.MetaDataObject.TaskForm import TaskForm
from v8unpack.unittest_helper import compare_file, NotEqualLine


class TestDecodeBraceFile(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data/form')
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
        uuid = 'f911d395-6098-48a3-911e-a41cab530f35'
        result = self.decode_raw_data(uuid)
        self.assertEqual('', result)

    def decode_raw_data(self, file_name):
        helper.clear_dir(self.temp_dir)
        decoder = TaskForm.decode(self.data_dir, file_name, self.temp_dir, '', 803)
        Form.encode(self.temp_dir, file_name, self.temp_dir2, 803)
        problems = ''
        try:
            result = compare_file(
                os.path.join(self.data_dir, file_name),
                os.path.join(self.temp_dir2, file_name),
                problems
            )
        except NotEqualLine as err:
            result = err
        print(result)

    def test_decode_by_scheme(self):
        from v8unpack.MetaDataObject.schemes.Form import Form

        file_name = '9c80a4da-8f1f-48ae-915c-4227fef8f364'
        data = Form(self.data_dir, file_name).decode()
