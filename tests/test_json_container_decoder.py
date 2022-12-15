import os
import sys
import unittest

sys.path.append("../../src/")
from v8unpack import helper
from v8unpack.json_container_decoder import JsonContainerDecoder
from v8unpack.unittest_helper import compare_file, NotEqualLine


class TestFileOrganizerCE(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data')
        self.temp_dir = os.path.join(self.data_dir, 'temp')
        self.temp_dir2 = os.path.join(self.data_dir, 'temp2')

    def test_decode_raw_text_json_object(self):
        helper.clear_dir(self.temp_dir)
        res = JsonContainerDecoder.decode([self.data_dir, 'raw_text_json_object', self.temp_dir])
        pass

    def test_decode_raw_text_json_object_no_format(self):
        helper.clear_dir(self.temp_dir)
        res = JsonContainerDecoder.decode([self.data_dir, 'raw_text_json_object_no_format', self.temp_dir])
        pass

    def test_decode_raw_text_json_array(self):
        helper.clear_dir(self.temp_dir)
        res = JsonContainerDecoder.decode([self.data_dir, 'raw_text_json_array', self.temp_dir])
        pass

    def test_decode_raw_text_bin(self):
        helper.clear_dir(self.temp_dir)
        res = JsonContainerDecoder.decode([self.data_dir, 'raw_text_bin', self.temp_dir])
        pass

    def test_decode_raw_b64_and_string(self):
        file_name = '041e0f14-4650-472f-ab76-bc17d5000d3d.0'
        helper.clear_dir(self.temp_dir)
        helper.clear_dir(self.temp_dir2)
        res1 = JsonContainerDecoder.decode([self.data_dir, file_name, self.temp_dir])
        JsonContainerDecoder.encode([self.temp_dir, f'{file_name}.json', self.temp_dir2])
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
