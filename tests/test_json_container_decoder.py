import os
import shutil
import json
import unittest

from v8unpack import helper
from v8unpack.json_container_decoder import JsonContainerDecoder


class TestFileOrganizerCE(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data')
        self.temp_dir = os.path.join(self.data_dir, 'temp')

    def test_decode_raw_text_json_object(self):
        helper.clear_dir(self.temp_dir)
        res = JsonContainerDecoder.decode(self.data_dir, 'raw_text_json_object')
        pass

    def test_decode_raw_text_json_object_no_format(self):
        helper.clear_dir(self.temp_dir)
        res = JsonContainerDecoder.decode(self.data_dir, 'raw_text_json_object_no_format')
        pass

    def test_decode_raw_text_json_array(self):
        helper.clear_dir(self.temp_dir)
        res = JsonContainerDecoder.decode(self.data_dir, 'raw_text_json_array')
        pass

    def test_decode_raw_text_bin(self):
        helper.clear_dir(self.temp_dir)
        res = JsonContainerDecoder.decode(self.data_dir, 'raw_text_bin')
        pass

    def test_decode_raw_b64_and_string(self):
        file_name = 'raw_b64_and_string'
        with open(os.path.join(self.data_dir, file_name), 'r', encoding='utf-8-sig') as entry_file:  # replace BOM
            source = entry_file.read()
        decode = JsonContainerDecoder.decode(self.data_dir, file_name)
        encode = JsonContainerDecoder().encode_root_object(decode)
        self.assertEqual(source, encode)
        # json_res = json.loads(res.encode(encoding='utf-8'))
        pass