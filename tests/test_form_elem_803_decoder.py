import os
import sys
import unittest

sys.path.append("../../src/")
from v8unpack import helper
from v8unpack.MetaDataObject.versions.Form803 import Form803
from v8unpack.unittest_helper import compare_file, NotEqualLine


class TestFileOrganizerCE(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data/form_elem_803')
        self.temp_dir = os.path.join(self.data_dir, 'temp')
        self.temp_dir2 = os.path.join(self.data_dir, 'temp2')

    def test_decode_all_form_elem(self):
        test_files = os.listdir(self.data_dir)
        result = ''
        for file_name in test_files:
            if file_name == 'temp':
                continue
            uuid, x, y = file_name.split('.')
            result += self.decode_form_elem(uuid)
        self.assertEqual('', result)

    def test_decode_form_elem(self):
        uuid = '29ecd407-e446-407e-8321-6de183302fd6'
        result = self.decode_form_elem(uuid)
        self.assertEqual('', result)

    def decode_form_elem(self, uuid):
        file_name = f'{uuid}.0.json'
        helper.clear_dir(self.temp_dir)
        form803 = Form803()
        form803.new_dest_dir = self.temp_dir
        form803.form = [helper.json_read(self.data_dir, file_name)]
        form803.decode_includes(None, self.temp_dir, '', None)

        form803.write_decode_object(self.temp_dir, '', uuid, 803)
        form803.encode_includes(self.temp_dir, uuid, self.temp_dir, 803)
        helper.json_write(form803.form[0], self.temp_dir, f'{uuid}.0.json')
        problems = ''
        try:
            result = compare_file(
                os.path.join(self.data_dir, file_name),
                os.path.join(self.temp_dir, file_name),
                problems
            )
        except NotEqualLine as err:
            result = err
        if result:
            print(result)
        return result
