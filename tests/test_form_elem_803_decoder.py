import os
import sys
import unittest

sys.path.append("../../src/")
from v8unpack import helper
from v8unpack.MetaDataObject.versions.Form803 import Form803
from v8unpack.MetaDataObject.versions.Form802 import Form802
from v8unpack.unittest_helper import compare_file, NotEqualLine


class TestFormElem803(unittest.TestCase):
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
            uuid, x = file_name.split('.')
            result += self.decode_form_elem(uuid)
        self.assertEqual('', result)

    def test_decode_form_elem(self):
        uuid = '0950028f-1316-4cc2-b5ef-1c2452770ce7'
        result = self.decode_form_elem(uuid)
        self.assertEqual('', result)

    def decode_form_elem(self, uuid):
        file_name = f'{uuid}.0'
        helper.clear_dir(self.temp_dir)
        raw_data = helper.brace_file_read(self.data_dir, file_name)

        form = Form802() if raw_data[0][0] == '2' else Form803()
        form.new_dest_dir = self.temp_dir
        form.form = [raw_data]
        form.decode_includes(None, self.temp_dir, '', None)

        form.write_decode_object(self.temp_dir, '', uuid, 803)
        form.encode_includes(self.temp_dir, uuid, self.temp_dir, 803)
        helper.brace_file_write(form.form[0], self.temp_dir, f'{uuid}.0')
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
