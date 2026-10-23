import base64
import unittest

from v8unpack.json_container_decoder import JsonContainerDecoder


class TestBase64Detection(unittest.TestCase):
    def encode(self, value):
        return JsonContainerDecoder().encode_root_object([[value]])

    def test_long_quoted_text_is_not_wrapped(self):
        value = '"Convert the user action log into the 1C:Enterprise script scenario"'
        self.assertEqual(len(value), 68)
        self.assertEqual(self.encode(value), '{' + value + '}')

    def test_plain_base64_remains_wrapped_and_decodable(self):
        payload = bytes(range(256))
        value = base64.b64encode(payload).decode('ascii')
        encoded = self.encode(value)[1:-1]
        lines = encoded.split('\n')
        self.assertGreater(len(lines), 1)
        self.assertTrue(all(len(line) == 64 for line in lines[:-1]))
        self.assertEqual(base64.b64decode(''.join(lines), validate=True), payload)

    def test_explicit_base64_remains_wrapped_and_decodable(self):
        payload = bytes(range(256))
        value = base64.b64encode(payload).decode('ascii')
        encoded = self.encode('#base64:' + value)[1:-1]
        self.assertTrue(encoded.startswith('#base64:'))
        self.assertIn('\n', encoded)
        self.assertEqual(base64.b64decode(encoded[len('#base64:'):].replace('\n', ''),
                                         validate=True), payload)

    def test_explicit_single_line_base64_is_not_wrapped(self):
        value = base64.b64encode(bytes(range(256))).decode('ascii')
        self.assertEqual(self.encode('##base64:' + value), '{#base64:' + value + '}')


if __name__ == '__main__':
    unittest.main()
