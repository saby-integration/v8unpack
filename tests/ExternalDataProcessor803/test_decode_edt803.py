import os
import shutil
import sys
import unittest

sys.path.append("../../src/")
from v8unpack.unittest_helper import HelperTestDecode


class TestDecode(HelperTestDecode):
    processes = 1  # uncomment for debug

    def setUp(self):
        super(TestDecode, self).setUp()
        self.src_dir = os.path.dirname(__file__)
        self.dest_dir = os.path.join(self.src_dir, 'src')
        self.src_file = 'ВнешняяОбработка803.epf'

        self.init(
            index_file_name='index.json',
            version='803'
        )
        pass

    def test_01_decode_stage0(self):
        super(TestDecode, self).decode_stage0()

    def test_01_decode_stage1(self):
        super(TestDecode, self).decode_stage1()

    def test_03_decode_stage3(self):
        super(TestDecode, self).decode_stage3()
        self.assert_external_data_processor_decode_stage3()

    def test_04_decode_stage4(self):
        # shutil.rmtree(os.path.join(self.test_dir, 'decodeCodeSubmodule'), ignore_errors=True)
        super(TestDecode, self).decode_stage4()

    def test_05_encode_stage4(self):
        super(TestDecode, self).encode_stage4()

    def test_06_encode_stage3(self):
         super(TestDecode, self).encode_stage3()

    def test_08_encode_stage1(self):
        super(TestDecode, self).encode_stage1()

    def test_09_encode_stage0(self):
        super(TestDecode, self).encode_stage0()

    @unittest.skip
    def test_extract_all(self):
        super(TestDecode, self).extract_all('./product.json', 'ВнешняяОбработка803.epf')

    @unittest.skip
    def test_build_all(self):
        super(TestDecode, self).build_all('./product.json', 'ВнешняяОбработка803.epf')

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
