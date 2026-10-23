import base64
import json
import tempfile
import unittest
from pathlib import Path

from v8unpack import helper
from v8unpack.json_container_decoder import JsonContainerDecoder


class TestStringNewlines(unittest.TestCase):
    def assert_readers(self, raw, expected, encoding='utf-8-sig'):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'sample').write_bytes(raw.encode(encoding))
            self.assertEqual(helper.brace_file_read(folder, 'sample'), expected)
            JsonContainerDecoder.decode((folder, 'sample', folder))
            self.assertEqual(json.loads((root / 'sample.json').read_text()), expected)
            JsonContainerDecoder.encode((folder, 'sample.json', folder))
            self.assertEqual(helper.brace_file_read(folder, 'sample'), expected)

    def test_structural_newlines_do_not_drop_nested_objects(self):
        for separator in ('\n', '\r\n', '\r'):
            with self.subTest(separator=repr(separator)):
                self.assert_readers('{1,"a",' + separator + '{2}}',
                                    [['1', '"a"', ['2']]])

    def test_structural_and_quoted_newlines_are_independent(self):
        for separator in ('\n', '\r\n', '\r'):
            for encoding in ('utf-8-sig', 'windows-1251'):
                with self.subTest(separator=repr(separator), encoding=encoding):
                    self.assert_readers('{1,"а\r\r\nб",' + separator + '{2}}',
                                        [['1', '"а\r\r\nб"', ['2']]], encoding)

    def test_multiline_base64_has_no_structural_newlines_in_its_value(self):
        payload = bytes(range(256))
        value = base64.b64encode(payload).decode('ascii')
        for separator in ('\n', '\r\n', '\r'):
            for prefix in ('', '#base64:'):
                with self.subTest(separator=repr(separator), prefix=prefix):
                    lines = [value[i:i + 64] for i in range(0, len(value), 64)]
                    raw = '{' + prefix + (separator * 2).join(lines) + separator + '}'
                    self.assert_readers(raw, [[prefix + value]])

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
