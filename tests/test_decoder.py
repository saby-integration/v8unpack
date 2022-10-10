import os
import sys
import unittest

sys.path.append("../../src/")
from v8unpack.MetaDataObject.CommonForm import CommonForm
from v8unpack.MetaDataObject.versions.Template803 import Template803 as Meta

class TestFileOrganizerCE(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data')
        self.temp_dir = os.path.join(self.data_dir, 'temp')

    def test_near(self):
        form = Meta()
        form.decode(self.data_dir, "cb225ac1-0acf-4807-aae2-0e135699ea05", self.temp_dir, "cb225ac1-0acf-4807-aae2-0e135699ea05", 803)
