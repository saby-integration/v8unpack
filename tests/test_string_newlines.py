import json
import tempfile
import unittest
from pathlib import Path

from v8unpack import helper
from v8unpack.json_container_decoder import JsonContainerDecoder


class TestStringNewlines(unittest.TestCase):
    def test_readers_and_writer_preserve_quoted_newlines(self):
        values = ['a\nb', 'a\r\nb', 'a\r\r\nb', 'a\n\nb',
                  'a\r\r\n\r\r\nb', 'a\r\r\n"quoted"\r\r\nb',
                  'a\rb', '\r\r\na\r\r\n']
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for index, value in enumerate(values):
                with self.subTest(value=repr(value)):
                    name = str(index)
                    quoted = '"' + value.replace('"', '""') + '"'
                    raw = '{1,' + quoted + ',\r\n{2}}'
                    (root / name).write_bytes(b'\xef\xbb\xbf' + raw.encode())
                    expected = [['1', quoted, ['2']]]
                    self.assertEqual(helper.brace_file_read(folder, name), expected)
                    JsonContainerDecoder.decode((folder, name, folder))
                    data = json.loads((root / (name + '.json')).read_text())
                    self.assertEqual(data, expected)
                    JsonContainerDecoder.encode((folder, name + '.json', folder))
                    rebuilt = (root / name).read_bytes().decode('utf-8-sig')
                    self.assertIn(quoted, rebuilt)
                    self.assertEqual(helper.brace_file_read(folder, name), expected)


if __name__ == '__main__':
    unittest.main()
