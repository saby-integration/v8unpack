import os
import sys
from v8unpack.json_container_decoder import test_decode_encode
from v8unpack import helper
import unittest


class TestJsonDecoder(unittest.TestCase):
    def setUp(self) -> None:
        self.src_dir = os.path.join(sys.path[0], 'decode_stage_1')
        self.temp_dir = os.path.join(sys.path[0], 'decode_stage_2/temp')

    def test_decode_extension(self):
        test_decode_encode(self, self.src_dir, 'b3e1e803-98b6-473e-972d-2149dc994a13')
        pass

    def test_decode_config_info(self):
        helper.clear_dir(self.temp_dir)
        test_decode_encode(self, self.src_dir, 'configinfo', self.temp_dir)
        helper.clear_dir(self.temp_dir)
        pass



