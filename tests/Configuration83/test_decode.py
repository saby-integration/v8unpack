import os
import sys
import shutil
import unittest
from v8unpack.unittest_helper import HelperTestDecode


class TestDecode(HelperTestDecode):
    def setUp(self):
        super(TestDecode, self).setUp()
        self.src_dir = os.path.join(sys.path[0])
        self.src_file = '1Cv8.cf'
        self.test_dir = os.path.join(sys.path[0], 'tmp')
        # self.version = '81'
        self.result = {
            'count_root_files_stage1': 18,
            'count_root_files_stage3': 7,
            'count_root_files_stage4': 7,
        }
        self.init()
        pass

    def test_01_decode_stage1(self):
        super(TestDecode, self).decode_stage1()

    def test_02_decode_stage2(self):
        super(TestDecode, self).decode_stage2()

    def test_03_decode_stage3(self):
        super(TestDecode, self).decode_stage3()

    def test_04_decode_stage4(self):
        shutil.rmtree(os.path.join(sys.path[0], 'decodeCodeSubmodule'), ignore_errors=True)
        super(TestDecode, self).decode_stage4()

    def test_05_encode_stage4(self):
        super(TestDecode, self).encode_stage4()

    def test_06_encode_stage3(self):
        super(TestDecode, self).encode_stage3()

    def test_07_encode_stage2(self):
        super(TestDecode, self).encode_stage2()

    def test_08_encode_stage1(self):
        super(TestDecode, self).encode_stage1()


if __name__ == '__main__':
    unittest.main()
