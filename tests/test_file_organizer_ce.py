import unittest
import os
from v8unpack import helper
from v8unpack.file_organizer_ce import FileOrganizerCE


class TestFileOrganizerCE(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.test_data_dir = os.path.join(self.current_dir, 'data')

    def test_1(self):

        src_path= src_file_name, dest_path, dest_file_name, descent = None
        FileOrganizerCE._unpack_file(src_path, src_file_name, dest_path, dest_file_name, descent=None)