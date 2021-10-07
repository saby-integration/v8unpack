import unittest
from v8unpack import helper


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
