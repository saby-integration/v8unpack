import os
import sys
import unittest

sys.path.append("../../src/")
from v8unpack.MetaDataObject.CommonForm import CommonForm


class TestFileOrganizerCE(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data')
        self.temp_dir = os.path.join(self.data_dir, 'temp')

    def test_near(self):
        form = CommonForm()
        form.decode(self.data_dir, "decode2", self.temp_dir, "", 803)
