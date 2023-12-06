import os
import sys
import unittest

sys.path.append("../../src/")
from v8unpack.unittest_helper import HelperTestDecode


class TestDecode(HelperTestDecode):
    # processes = 1  # uncomment for debug

    def setUp(self):
        super(TestDecode, self).setUp()
        self.src_dir = os.path.dirname(__file__)
        self.src_file = 'Расширение1.cfe'
        self.init(
            auto_include=True,
            version='80313'
        )
        pass

    def test_01_decode_stage0(self):
        super(TestDecode, self).decode_stage0()

    def test_01_decode_stage1(self):
        super(TestDecode, self).decode_stage1()

    def test_03_decode_stage3(self):
        super(TestDecode, self).decode_stage3()

    def test_04_decode_stage4(self):
        # shutil.rmtree(os.path.join(sys.path[0], 'decodeCodeSubmodule'), ignore_errors=True)
        super(TestDecode, self).decode_stage4()

    def test_05_encode_stage4(self):
        super(TestDecode, self).encode_stage4()

    def test_06_encode_stage3(self):
        super(TestDecode, self).encode_stage3()

    def test_08_encode_stage1(self):
        super(TestDecode, self).encode_stage1()

    def test_09_encode_stage0(self):
        super(TestDecode, self).encode_stage0()


if __name__ == '__main__':
    unittest.main()
