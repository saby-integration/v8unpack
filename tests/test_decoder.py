import os
import sys
import unittest

sys.path.append("../../src/")
from v8unpack.MetaDataObject.Role import Role as Meta
from v8unpack import helper


class TestFileOrganizerCE(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data', 'json_decode_src')
        self.temp_dir = os.path.join(self.data_dir, 'temp')

    def test_near(self):
        form = Meta()
        file_name = "8a310493-c06f-46db-b2b5-14d6ed203312"
        # os.remove(os.path.join(self.temp_dir, file_name))
        helper.clear_dir(os.path.join(self.temp_dir, file_name))
        form.decode(self.data_dir, file_name, self.temp_dir, file_name, 803)
