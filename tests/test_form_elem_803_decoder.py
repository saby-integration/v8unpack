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
        self.data_dir = os.path.join(self.current_dir, 'data', 'form_elem_803')
        self.temp_dir = os.path.join(self.data_dir, 'temp')
        self.temp_dir2 = os.path.join(self.data_dir, 'temp2')

    def test_decode_all_form_elem(self):
        test_files = os.listdir(self.data_dir)
        result = ''
        for file_name in test_files:
            if file_name == 'temp':
                continue
            item = file_name.split('.')
            result += self.decode_form_elem(item[0])
        self.assertEqual('', result)

    def test_decode_form_elem(self):
        uuid = '66f22eef-9167-4661-acc1-769de41ab428'
        result = self.decode_form_elem(uuid)
        self.assertEqual('', result)

    def decode_form_elem(self, uuid):
        file_name = f'{uuid}.0'
        json_file_name = f'{file_name}.json'
        helper.clear_dir(self.temp_dir)
        if not os.path.isfile(os.path.join(self.data_dir, json_file_name)):
            raw_data = helper.brace_file_read(self.data_dir, file_name)
            helper.json_write(raw_data, self.data_dir, json_file_name)
            os.remove(os.path.join(self.data_dir, file_name))
        else:
            raw_data = helper.json_read(self.data_dir, json_file_name)
        form = Form802() if raw_data[0][0] == '2' else Form803()
        form.new_dest_dir = self.temp_dir
        form.form = [raw_data]
        form.decode_includes(None, self.temp_dir, '', None)

        form.write_decode_object(self.temp_dir, '', uuid)
        form.encode_nested_includes(self.temp_dir, uuid, self.temp_dir, '')
        helper.json_write(form.form[0], self.temp_dir, json_file_name)
        problems = ''
        try:
            result = compare_file(
                os.path.join(self.data_dir, json_file_name),
                os.path.join(self.temp_dir, json_file_name),
                problems
            )
        except NotEqualLine as err:
            result = str(err)
        if result:
            print(result)
        return result
