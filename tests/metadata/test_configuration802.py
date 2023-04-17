import os
import sys
import unittest

sys.path.append("../../src/")
from v8unpack.MetaObject.Configuration802 import Configuration802
from v8unpack.decoder import Decoder
from v8unpack.helper import clear_dir


class TestTemplate(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data')
        self.temp_dir = os.path.join(self.current_dir, 'temp')
        self.temp_dir2 = os.path.join(self.current_dir, 'temp2')

    def test_decode(self):
        clear_dir(self.temp_dir)
        clear_dir(self.temp_dir2)
        Configuration802.decode(self.data_dir, self.temp_dir)
        Configuration802.encode(self.temp_dir, self.temp_dir2)


