import os
import shutil
import sys
import unittest

from v8unpack import helper
from v8unpack.unittest_helper import HelperTestDecode


class TestDecodeC803(HelperTestDecode):
    pool = helper.get_pool(pool=None, processes=1)

    def setUp(self):
        super().setUp()
        self.src_dir = os.path.dirname(__file__)
        self.src_file = '1Cv8.cf'
        # self.version = '801'
        self.result = {
            # 'count_root_files_stage1': 40,
            # 'count_root_files_stage3': 10,
            # 'count_root_files_stage4': 10,
        }
        self.init()
        pass

    def test_01_decode_stage0(self):
        super().decode_stage0()

    def test_01_decode_stage1(self):
        super().decode_stage1()

    def test_02_decode_stage2(self):
        super().decode_stage2()

    def test_03_decode_stage3(self):
        super().decode_stage3()

    def test_04_decode_stage4(self):
        shutil.rmtree(os.path.join(sys.path[0], 'decodeCodeSubmodule'), ignore_errors=True)
        super().decode_stage4()

    def test_05_encode_stage4(self):
        super().encode_stage4()

    def test_06_encode_stage3(self):
        super().encode_stage3()

    def test_07_encode_stage2(self):
        super().encode_stage2()

    def test_08_encode_stage1(self):
        super().encode_stage1()

    def test_09_encode_stage0(self):
        super().encode_stage0()

    @unittest.skip
    def test_extract(self):
        from v8unpack.v8unpack import extract, build
        extract('ВнешняяОбработка803.epf', 'src')
        build('src', 'ВнешняяОбработка.build.epf')

    @unittest.skip
    def test_create_index(self):
        from v8unpack.index import update_index
        update_index(self.decode_dir_stage4, os.path.join(sys.path[0], 'tmp', 'index.json'),
                     'decodeCodeSubmodule')


if __name__ == '__main__':
    unittest.main()
