import os
import shutil
import sys
import unittest

sys.path.append("../../src/")
from v8unpack import helper
from v8unpack.organizer_file import OrganizerFile
from v8unpack.organizer_code import OrganizerCode


class TestCodeOrganizer(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data')
        self.temp_src_dir = os.path.join(self.data_dir, 'temp_src')
        self.temp_dest_dir = os.path.join(self.data_dir, 'temp_dest/src')
        self.temp_dest_dir2 = os.path.join(self.data_dir, 'temp_dest2/src')

    def test_1(self):
        src_file_name = 'code.bsl'
        helper.clear_dir(self.temp_src_dir)
        helper.clear_dir(self.temp_dest_dir)
        helper.clear_dir(self.temp_dest_dir2)
        copy_source(self.data_dir, self.temp_src_dir, ['code.bsl', 'code_include1.bsl', 'code_include2.bsl'])
        unpack_params = (self.temp_src_dir, '', src_file_name, self.temp_dest_dir, None, None)
        OrganizerFile.unpack_code_file(unpack_params)
        # src_dir, src_path, src_file_name, dest_dir, dest_path, dest_file_name, index_code_areas, \
        #         descent, pack_get_descent_filename
        pack_params = (self.temp_dest_dir, '', src_file_name, self.temp_dest_dir2, '', src_file_name, None, None,
                       OrganizerFile.pack_get_descent_filename)
        OrganizerCode.pack(pack_params)


def copy_source(src_path, dest_path, files):
    for file_name in files:
        shutil.copy(
            os.path.join(src_path, file_name),
            os.path.join(dest_path, file_name),
        )
