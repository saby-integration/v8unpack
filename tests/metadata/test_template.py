import os
import sys
import unittest

sys.path.append("../../src/")
# from v8unpack.MetaDataObject.versions.Template803 import Meta
from v8unpack.decoder import Decoder
from v8unpack.helper import clear_dir


class TestTemplate(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data')
        self.temp_dir = os.path.join(self.current_dir, 'temp')
        clear_dir(self.temp_dir)

    def test_decode(self):
        Decoder.decode_include(['Template', [
            self.data_dir, '02f0dbd6-4bb9-4fdb-9c02-116da924943f', self.temp_dir, '', '803']])


