import os
import shutil
import struct
import sys
import unittest

sys.path.append('../../src/')
from v8unpack import helper
from v8unpack.container_reader import extract, decompress_and_extract
from v8unpack.decoder import decode, encode
from v8unpack.MetaDataObject.Template import Template2


class TestSchemeTemplate(unittest.TestCase):
    """Макет схемы компоновки данных должен раскладываться на xml и собираться обратно."""

    def setUp(self):
        self.src_dir = os.path.dirname(os.path.abspath(__file__))
        self.src_file = 'ВнешнийОтчёт803.erf'
        self.test_dir = os.path.join(self.src_dir, 'tmp')
        helper.clear_dir(self.test_dir)
        self.decode_dir_stage0 = os.path.join(self.test_dir, 'decode_stage_0')
        self.decode_dir_stage1 = os.path.join(self.test_dir, 'decode_stage_1')
        self.decode_dir_stage3 = os.path.join(self.test_dir, 'decode_stage_3')
        self.encode_dir_stage1 = os.path.join(self.test_dir, 'encode_stage_1')

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _decode(self):
        extract(os.path.join(self.src_dir, self.src_file), self.decode_dir_stage0, False, False)
        decompress_and_extract(self.decode_dir_stage0, self.decode_dir_stage1)
        decode(self.decode_dir_stage1, self.decode_dir_stage3, pool=None, options={})
        return os.path.join(self.decode_dir_stage3, 'Template', 'ОсновнаяСхемаКомпоновкиДанных')

    def test_scheme_template_decode(self):
        tpl_dir = self._decode()

        schema_path = os.path.join(tpl_dir, 'Template.xml')
        self.assertTrue(os.path.isfile(schema_path), 'Схема не выложена в Template.xml')
        self.assertTrue(os.path.isfile(os.path.join(tpl_dir, 'Template.settings1.xml')))
        self.assertTrue(os.path.isfile(os.path.join(tpl_dir, 'Template.tail.xml')))
        self.assertFalse(os.path.isfile(os.path.join(tpl_dir, 'Template.bin')),
                         'Макет схемы остался бинарником')

        with open(schema_path, encoding='utf-8-sig') as file:
            schema = file.read()
        self.assertIn('<dataCompositionSchema', schema)
        self.assertIn('<query>', schema)

    def test_scheme_template_round_trip(self):
        tpl_dir = self._decode()

        uuid = helper.json_read(tpl_dir, 'Template.id.json')['uuid']
        source_data = helper.bin_read(os.path.join(self.decode_dir_stage1, '0'), f'{uuid}.0')

        encode(self.decode_dir_stage3, self.encode_dir_stage1, pool=None, options={})
        encode_data = helper.bin_read(os.path.join(self.encode_dir_stage1, '0'), f'{uuid}.0')

        self.assertEqual(source_data, encode_data, 'Макет схемы после сборки отличается от исходного')

    def test_split_pack(self):
        schema = b'\xef\xbb\xbf<?xml version="1.0" encoding="UTF-8"?>\r\n<SchemaFile/>'
        settings = b'\xef\xbb\xbf<?xml version="1.0" encoding="UTF-8"?>\r\n<Settings/>'
        tail = b'\xef\xbb\xbf<?xml version="1.0" encoding="UTF-8"?>\r\n<SchemaFile/>'
        raw = (struct.pack('<II', 0, 1)
               + struct.pack('<QQ', len(schema), len(settings))
               + schema + settings + tail)

        parts = Template2._skd_split(raw)
        self.assertEqual(parts, [schema, settings, tail])
        self.assertEqual(Template2._skd_part_names(len(parts) - 2),
                         ['xml', 'settings1.xml', 'tail.xml'])
        self.assertEqual(Template2._skd_pack(parts), raw)

    def test_split_garbage(self):
        self.assertIsNone(Template2._skd_split(b'not a scheme'))
        self.assertIsNone(Template2._skd_split(b'\x00\x00'))


if __name__ == '__main__':
    unittest.main()
