import os
import sys
import unittest

sys.path.append("../../src/")
from v8unpack.decoder import Decoder
from v8unpack import helper


class TestDecoder(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data', 'json_decode_src')
        self.temp_dir = os.path.join(self.data_dir, 'temp')

    def test_decode_include(self):
        params = [
            'AccountingRegister',
            ['C:\\project\\v8unpack\\tests_tmp\\erp2\\tmp\\decode_stage_1\\1', '7b248429-2107-4371-b371-a099028cd179',
             'C:\\project\\v8unpack\\tests_tmp\\erp2\\tmp\\decode_stage_3', 'AccountingRegister', {'version': '803'}]]
        tasks = Decoder.decode_include(params)
