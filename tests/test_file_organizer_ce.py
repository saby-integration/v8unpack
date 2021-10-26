import os
import shutil
import unittest

from v8unpack import helper
from v8unpack.file_organizer_ce import FileOrganizerCE


class TestFileOrganizerCE(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.current_dir, 'data')
        self.temp_dir = os.path.join(self.data_dir, 'temp')

    def test_near(self):
        helper.clear_dir(self.temp_dir)
        self.copy_data_to_temp('test.obj.1c', ['3000070060', '3000075100', '3000088001'])

        _path, _file_name = helper.get_near_descent_file_name(self.temp_dir, 'test.obj.1c', 3000075100)
        self.assertEqual(self.temp_dir, _path)
        self.assertEqual('test.obj.3000075100.1c', _file_name)
        _path, _file_name = helper.get_near_descent_file_name(self.temp_dir, 'test.obj.1c', 3000088003)
        self.assertEqual(self.temp_dir, _path)
        self.assertEqual('test.obj.3000088001.1c', _file_name)
        _path, _file_name = helper.get_near_descent_file_name(self.temp_dir, 'test.obj.1c', 1)
        self.assertEqual('', _path)
        self.assertEqual('', _file_name)
        _path, _file_name = helper.get_near_descent_file_name(self.temp_dir, 'test.2.obj.1c', 1)
        self.assertEqual('', _path)
        self.assertEqual('', _file_name)

    def test_1(self):
        helper.clear_dir(self.temp_dir)
        self.copy_data_to_temp('test.1c', ['3000070060', '3000075100', '3000088001'], '')

        FileOrganizerCE._unpack_file(self.data_dir, 'test.1c', self.temp_dir, 'test.1c', descent=3000088001)

        self.assertEqual(
            os.path.getsize(os.path.join(self.data_dir, 'test.1c')),
            os.path.getsize(os.path.join(self.temp_dir, 'test.3000088001.1c'))
        )

        FileOrganizerCE._unpack_file(self.data_dir, 'test.1c', self.temp_dir, 'test.1c', descent=3000075101)
        self.assertEqual(
            os.path.getsize(os.path.join(self.data_dir, 'test.1c')),
            os.path.getsize(os.path.join(self.temp_dir, 'test.3000075101.1c'))
        )

        self.copy_data_to_temp('test.obj.1c', ['3000070060'])
        FileOrganizerCE._unpack_file(self.data_dir, 'test.obj.1c', self.temp_dir, 'test.obj.1c', descent=3000070061)
        self.assertRaises(
            FileNotFoundError,
            lambda: os.path.getsize(os.path.join(self.temp_dir, 'test.obj.3000070061.1c'))
        )
        self.assertEqual(
            os.path.getsize(os.path.join(self.data_dir, 'test.obj.1c')),
            os.path.getsize(os.path.join(self.temp_dir, 'test.obj.3000070060.1c'))
        )

    def copy_data_to_temp(self, src_file_name, descents: list, value=None):
        for descent in descents:
            dest_file_name = helper.get_descent_file_name(src_file_name, descent)
            dest_full_path = os.path.join(self.temp_dir, dest_file_name)
            shutil.copy(
                os.path.join(self.data_dir, src_file_name),
                dest_full_path
            )
            if value is not None:
                with open(dest_full_path, 'w', encoding='utf-8') as file:
                    file.write('')
