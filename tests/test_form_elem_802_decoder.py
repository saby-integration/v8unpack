import os
import sys
import unittest

sys.path.append("../../src/")
from v8unpack import helper
from v8unpack.MetaDataObject.versions.Form803 import Form803
from v8unpack.MetaDataObject.versions.Form802 import Form802
from v8unpack.unittest_helper import compare_file, NotEqualLine


class TestFormElem802(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data', 'form82')
        self.temp_dir = os.path.join(self.data_dir, 'temp')
        self.temp_dir2 = os.path.join(self.data_dir, 'temp2')

    def test_convert_to_json(self):
        test_files = os.listdir(self.data_dir)
        for file_name in test_files:
            if os.path.isdir(os.path.join(self.data_dir,file_name)):
                continue
            json_file_name = f'{file_name}.json'
            raw_data = helper.brace_file_read(self.data_dir, file_name)
            helper.json_write(raw_data, self.temp_dir, json_file_name)

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
        # file_name = 'СтраницыИПанели'
        # file_name = 'Фильтр'
        # file_name = '2 добавлена страница'
        # file_name = '4 страница 1 добавлена надпись'
        file_name = 'ДоПереносаПоля'
        file_name = 'ПослеПереносаПоля'
        file_name = 'ДоПереноса2'
        file_name = 'ПослеПереноса2'
        result = self.decode_form_elem(file_name)
        self.assertEqual('', result)

    def test_decode_form_elem7(self):
        file_name = 'form7'  # не панель страницы 01 поставлен ручной порядок обхода и изменен порядок 2 и 3 флагов
        result = self.decode_form_elem(file_name)

    def decode_form_elem(self, file_name):
        helper.clear_dir(self.temp_dir)
        json_origin_file_name = f'{file_name}.origin.json'
        json_result_file_name = f'{file_name}.result.json'
        raw_data = helper.brace_file_read(self.data_dir, file_name)
        helper.json_write(raw_data, self.temp_dir, json_origin_file_name)
        form = Form802(options=dict(auto_include=True))
        form.new_dest_dir = self.temp_dir
        form.form = [raw_data]
        form.decode_includes(None, self.temp_dir, '', None)
        form.write_decode_object(self.temp_dir, '', file_name)
        form.encode_nested_includes(self.temp_dir, file_name, self.temp_dir, '')
        helper.json_write(form.form[0], self.temp_dir, json_result_file_name)
        helper.brace_file_write(helper.json_read(self.temp_dir, json_result_file_name), self.temp_dir, file_name)
        problems = ''
        try:
            result = compare_file(
                os.path.join(self.temp_dir, json_origin_file_name),
                os.path.join(self.temp_dir, json_result_file_name),
                problems
            )
        except NotEqualLine as err:
            result = str(err)
        return result
