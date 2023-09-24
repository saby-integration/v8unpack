import sys
import unittest

from v8unpack import helper

sys.path.append("../../src/")


class TestHelper(unittest.TestCase):
    def test_get_extension_from_comment(self):
        data = [
            ("", "bin"),
            ("png", "png"),
            (" png ", "png"),
            ("Комментарий png", "png")
        ]
        for elem in data:
            self.assertEqual(elem[1], helper.get_extension_from_comment(elem[0]))

    def test_check_version(self):
        data = [
            ("12.1.1", "12.1.0", False),
            ("12.1.1", "12.1.1", False),
            ("12.1.1", "12.1.2", False),
            ("12.1.1", "13.1.1", True),
            ("12.1.1", "12.2.1", True),
            ("", "", True),
            ("F", "A", True),
            ("12.1.1", "", True),
            ("12.1.1", "d", True)
        ]
        for elem in data:
            try:
                helper.check_version(elem[0], elem[1])
                self.assertFalse(elem[2])
            except AssertionError:
                self.assertTrue(elem[2])
