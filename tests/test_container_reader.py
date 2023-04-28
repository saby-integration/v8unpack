import os
import sys
import unittest

sys.path.append("../../src/")
from v8unpack.container_reader import extract as container_extract, decompress_and_extract
from v8unpack.container_writer import build as container_build, compress_and_build


class TestFileOrganizerCE(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data')
        self.temp_dir = os.path.join(self.data_dir, 'temp')

    def test_extract_old(self):
        src_filename = os.path.join(self.data_dir, 'apam_old.cf')
        dest_dir0 = os.path.join(self.temp_dir, 'apam-0')
        dest_dir1 = os.path.join(self.temp_dir, 'apam-1')
        container_extract(src_filename, dest_dir0, False, False)
        decompress_and_extract(dest_dir0, dest_dir1)

    def test_extract_16(self):
        src_filename = os.path.join(self.data_dir, 'apam.cf')
        dst_filename = os.path.join(self.temp_dir, 'apam.cf')
        # src_filename = os.path.join(self.data_dir, 'apam_old.cf')
        # src_filename = os.path.join(self.data_dir, '1Cv8_8316.cf')
        dest_dir0 = os.path.join(self.temp_dir, 'apam16-0')
        dest_dir1 = os.path.join(self.temp_dir, 'apam16-1')
        dest_dir2 = os.path.join(self.temp_dir, 'apam16-2')
        # container_extract(src_filename, dest_dir0, False, False)
        # decompress_and_extract(dest_dir0, dest_dir1)
        compress_and_build(dest_dir1, dest_dir2)
        container_build(dest_dir2, dst_filename, True, version='80316')
