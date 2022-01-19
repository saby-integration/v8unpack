import os
import unittest

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
        file_name = 'raw_end_string'
        data = b'\xef\xbb\xbf{\r\n{"S1\r\r\n\t\tS2\r\n\t\tS2\r\r\n\t\t\tS3\r\r\n\tS4"},"MainTable",\r\n{#base64:AgFTS2/0iI3BT9l0HEdaFTS2/0iI3BT9l0HEdaFTS2/0iI3BT9l0HEdaFTS2/0iI3BT9l0HEdaFTS2/0iI3BT9l0HEdaFTS2/0iI3BT9l0HEdaFTS2/0iI3BT9l0HEdaFTS2/0iI3BT9l0HEdaFTS2/0iI3BT9l0HEdaFTS2/0iI3BT9l0HEdayG8=},\r\n{#base64:iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAA\n'
        with open(os.path.join(self.data_dir, 'raw_end_string'), 'wb') as file:
            file.write(data)
        helper.clear_dir(self.temp_dir)
        helper.clear_dir(self.temp_dir2)
        JsonContainerDecoder.decode(self.data_dir, file_name, self.temp_dir)
        JsonContainerDecoder.encode(self.temp_dir, f'{file_name}.json', self.temp_dir2)
        try:
            result = compare_file(
                os.path.join(self.data_dir, file_name),
                os.path.join(self.temp_dir2, file_name)
            )
        except NotEqualLine as err:
            result = err
        print(result)
        self.assertEqual('', result)
        # json_res = json.loads(res.encode(encoding='utf-8'))
        pass
