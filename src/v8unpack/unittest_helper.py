import json
import os
import sys
import unittest

from . import helper
from .container_reader import extract, decompress_and_extract
from .container_writer import build, compress_and_build
from .decoder import decode, encode, Decoder
from .file_organizer import FileOrganizer
from .file_organizer_ce import FileOrganizerCE
from .json_container_decoder import JsonContainerDecoder
from .json_container_decoder import json_decode, json_encode


class HelperTestDecode(unittest.TestCase):
    pool = None
    processes = None

    @classmethod
    def setUpClass(cls) -> None:
        if cls.pool is None:
            cls.pool = helper.get_pool()
        # cls.maxDiff = None

    # @classmethod
    # def tearDownClass(cls) -> None:
    #     helper.close_pool(cls.pool)

    def setUp(self) -> None:
        self.src_dir = os.path.join(sys.path[0])  # абсолютный путь до папки с исходным файлом
        self.src_file = ''  # имя исходного файла
        self.test_dir = ''  # абсолютный путь до временной папки c файлами промежуточных стадий
        self.dest_dir = ''
        self.result = None
        self.version = '803'
        self.index = None

    def init(self, **kwargs):
        if not self.test_dir:
            self.test_dir = os.path.join(self.src_dir, 'tmp')

        os.makedirs(self.test_dir, exist_ok=True)

        self.decode_dir_stage0 = self.get_decode_folder(0)
        self.decode_dir_stage1 = self.get_decode_folder(1)
        self.decode_dir_stage2 = self.get_decode_folder(2)
        self.decode_dir_stage3 = self.get_decode_folder(3)
        self.decode_dir_stage4 = self.dest_dir if self.dest_dir else self.get_decode_folder(4)

        self.encode_dir_stage0 = self.get_encode_folder(0)
        self.encode_dir_stage1 = self.get_encode_folder(1)
        self.encode_dir_stage2 = self.get_encode_folder(2)
        self.encode_dir_stage3 = self.get_encode_folder(3)

        index = kwargs.get('index')
        if index:
            with open(index, 'r', encoding='utf-8') as f:
                self.index = json.load(f)

        pass

    def get_decode_folder(self, stage):
        return os.path.join(self.test_dir, f'decode_stage_{stage}')

    def get_encode_folder(self, stage):
        return os.path.join(self.test_dir, f'encode_stage_{stage}')

    def decode_stage0(self):
        extract(os.path.join(self.src_dir, self.src_file), self.decode_dir_stage0, False, False)
        if self.result:
            files = os.listdir(self.decode_dir_stage0)
            self.assertEqual(len(files), self.result['count_root_files_stage1'], 'count_root_files_stage1')

    def decode_stage1(self):
        decompress_and_extract(self.decode_dir_stage0, self.decode_dir_stage1, pool=self.pool)
        if self.result:
            files = os.listdir(self.decode_dir_stage1)
            self.assertEqual(len(files), self.result['count_root_files_stage1'], 'count_root_files_stage1')

    def decode_stage2(self):
        json_decode(self.decode_dir_stage1, self.decode_dir_stage2, pool=self.pool)
        if self.result:
            files = os.listdir(self.decode_dir_stage2)
            self.assertEqual(len(files), self.result['count_root_files_stage1'], 'count_root_files_stage1')

    def decode_stage3(self):
        decode(self.decode_dir_stage2, self.decode_dir_stage3, pool=self.pool, version=self.version)
        if self.result:
            files = os.listdir(self.decode_dir_stage3)
            self.assertEqual(len(files), self.result['count_root_files_stage3'], 'count_root_files_stage3')

    def decode_stage4(self, descent=None):
        helper.clear_dir(os.path.normpath(self.decode_dir_stage4))
        if descent:
            FileOrganizerCE.unpack(self.decode_dir_stage3, self.decode_dir_stage4,
                                   pool=self.pool, index=self.index, descent=descent)
        else:
            FileOrganizer.unpack(self.decode_dir_stage3, self.decode_dir_stage4, pool=self.pool, index=self.index)
        if self.result:
            files = os.listdir(self.decode_dir_stage4)
            self.assertEqual(len(files), self.result['count_root_files_stage4'], 'count_root_files_stage4')
            pass

    def encode_stage4(self, descent=None):
        helper.clear_dir(os.path.normpath(self.encode_dir_stage3))
        if descent:
            FileOrganizerCE.pack(self.decode_dir_stage4, self.encode_dir_stage3,
                                 pool=self.pool, index=self.index, descent=descent)
        else:
            FileOrganizer.pack(self.decode_dir_stage4, self.encode_dir_stage3, pool=self.pool, index=self.index)
        if self.result:
            files = os.listdir(self.encode_dir_stage3)
            self.assertEqual(len(files), self.result['count_root_files_stage3'], 'count_root_files_stage3')

    def encode_stage3(self):
        encode(self.encode_dir_stage3, self.encode_dir_stage2, version=self.version, pool=self.pool)
        self.assert_stage(self.decode_dir_stage2, self.encode_dir_stage2)
        if self.result:
            files = os.listdir(self.encode_dir_stage2)
            self.assertEqual(len(files), self.result['count_root_files_stage1'])

    def encode_stage2(self):
        json_encode(self.encode_dir_stage2, self.encode_dir_stage1, pool=self.pool)
        self.assert_stage(self.decode_dir_stage1, self.encode_dir_stage1)
        if self.result:
            files = os.listdir(self.encode_dir_stage1)
            self.assertEqual(len(files), self.result['count_root_files_stage1'])

    def encode_stage1(self):
        compress_and_build(self.encode_dir_stage1, self.encode_dir_stage0, pool=self.pool)
        # self.assert_stage(self.decode_dir_stage0, self.encode_dir_stage0)
        if self.result:
            files = os.listdir(self.encode_dir_stage0)
            self.assertEqual(len(files), self.result['count_root_files_stage1'])

    def encode_stage0(self):
        # helper.clear_dir(os.path.normpath(self.test_dir))
        encode_file_path = os.path.join(self.test_dir, self.src_file)
        # decode_file_path = os.path.join(self.src_dir, self.src_file)
        build(self.encode_dir_stage0, encode_file_path, True)
        # self.assertByteFile(decode_file_path, encode_file_path)

    def assert_external_data_processor_decode_stage3(self):
        if self.result:
            form_files = os.listdir(os.path.join(self.decode_dir_stage3, 'Form'))
            self.assertEqual(len(form_files), self.result['count_forms_files'])
            template_files = os.listdir(os.path.join(self.decode_dir_stage3, 'Template'))
            self.assertEqual(len(template_files), self.result['count_templates_files'])

    def assert_stage(self, decode_dir, encode_dir):
        problems = self._assert_stage(decode_dir, encode_dir)
        self.assertTrue(not problems, f'file not equal\n{problems}')

    def _assert_stage(self, decode_dir, encode_dir):
        entries = os.listdir(decode_dir)
        problems = ''
        include_problems = ''
        for entry in entries:
            if entry.startswith('configinfo'):
                continue
            path_decode_entry = os.path.join(decode_dir, entry)
            path_encode_entry = os.path.join(encode_dir, entry)
            if os.path.isdir(path_decode_entry):
                include_problems += self._assert_stage(path_decode_entry, path_encode_entry)
            else:
                try:
                    problems += compare_file(path_decode_entry, path_encode_entry)
                except NotEqualLine as err:
                    problems += str(err)
        if problems:
            problems = f'   {decode_dir}\n   {encode_dir}{problems}\n'
        if include_problems:
            problems += '\n' + include_problems
        return problems

    @classmethod
    def remove_closing_brackets(cls, file_data):
        return file_data

    def tmpl_json_encode(self, *, encode_src_dir='', entity_name='', encode_dest_dir='', decode_dir=''):
        JsonContainerDecoder.encode(encode_src_dir, f'{entity_name}.json', encode_dest_dir)
        if decode_dir:
            self.assertUtfFile(
                os.path.join(encode_dest_dir, entity_name),
                os.path.join(decode_dir, entity_name)
            )

    # def tmpl_decode(self, *, encode_src_dir='', entity_name='', encode_dest_dir='', decode_dir=''):
    #     Decoder.decode(encode_src_dir, f'{entity_name}.json', encode_dest_dir)
    #     if decode_dir:
    #         self.assertUtfFile(
    #             os.path.join(encode_dest_dir, entity_name),
    #             os.path.join(decode_dir, entity_name)
    #         )

    def assertUtfFile(self, src, dest):
        with open(src, 'r', encoding='utf-8') as file:
            src_data = file.read()
        with open(dest, 'r', encoding='utf-8') as file:
            dest_data = file.read()
        self.assertEqual(dest_data, src_data)

    def assertByteFile(self, src, dest):
        with open(src, 'rb') as file:
            src_data = file.read()
        with open(dest, 'rb') as file:
            dest_data = file.read()
        self.assertEqual(dest_data, src_data)


class NotEqualLine(Exception):
    pass


def compare_file(path_decode_entry, path_encode_entry):
    problems = ''
    entry = os.path.basename(path_encode_entry)
    folder = os.path.basename(os.path.dirname(path_encode_entry))
    title = os.path.join(folder,entry)
    with open(path_decode_entry, 'rb') as decode_file:
        try:
            i = 0
            with open(path_encode_entry, 'rb') as encode_file:
                for decode_line in decode_file:
                    # if i == 1 and decode_line.startswith(b'\xef\xbb\xbf'):
                    #     decode_line = decode_line[3:]
                    i += 1
                    encode_line = encode_file.readline()
                    if decode_line != encode_line:
                        if encode_line.endswith(b'\r\n'):
                            if decode_line.endswith(b'\r\r\n') and decode_line[:-3] == encode_line[:-2]:
                                encode_file.readline()
                                # problems += f'\n      {entry:38} {i:6} \\r {decode_line}'
                                continue
                            if encode_line[:-2] == decode_line:
                                continue
                        problems += f'\n      {title:73} {i:5} {decode_line}'
                        problems += f'\n      {"":90} {encode_line}'
                        raise NotEqualLine(problems)
                    elif decode_line.hex() != encode_line.hex():
                        a = 1
                for encode_line in encode_file:
                    i += 1
                    if encode_line == b'}\r\n' or b'}':
                        continue
                    problems += f'\n      {entry:38} {i:6} {encode_line}'
                    raise NotEqualLine(problems)
        except FileNotFoundError:
            problems += f'\n      {entry} not encode file'
    return problems
