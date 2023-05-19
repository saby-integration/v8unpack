import json
import os
import sys
import unittest

from tqdm.auto import tqdm

from . import helper
from .container_reader import extract, decompress_and_extract
from .container_writer import build, compress_and_build
from .decoder import decode, encode
from .file_organizer import FileOrganizer
from .file_organizer_ce import FileOrganizerCE
from .json_container_decoder import JsonContainerDecoder


class HelperTestDecode(unittest.TestCase):
    pool = None
    processes = None

    def tearDown(self) -> None:
        helper.close_pool(self.pool)

    def setUp(self) -> None:
        if not sys.warnoptions:
            import warnings
            warnings.simplefilter("ignore")

        self.pool = helper.get_pool(processes=self.processes)
        self.src_dir = os.path.join(sys.path[0])  # абсолютный путь до папки с исходным файлом
        self.src_file = ''  # имя исходного файла
        self.test_dir = ''  # абсолютный путь до временной папки c файлами промежуточных стадий
        self.dest_dir = ''
        self.options = None
        self.result = None
        self.version = '803'
        self.index = None

    def init(self, *, index_file_name=None, **kwargs):
        if not self.test_dir:
            self.test_dir = os.path.join(self.src_dir, 'tmp')
        self.options = kwargs
        helper.makedirs(self.test_dir, exist_ok=True)

        self.decode_dir_stage0 = self.get_decode_folder(0)
        self.decode_dir_stage1 = self.get_decode_folder(1)
        self.decode_dir_stage2 = self.get_decode_folder(2)
        self.decode_dir_stage3 = self.get_decode_folder(3)
        self.decode_dir_stage4 = self.dest_dir if self.dest_dir else self.get_decode_folder(4)

        self.encode_dir_stage0 = self.get_encode_folder(0)
        self.encode_dir_stage1 = self.get_encode_folder(1)
        self.encode_dir_stage2 = self.get_encode_folder(2)
        self.encode_dir_stage3 = self.get_encode_folder(3)

        if index_file_name:
            self.index = helper.check_index(index_file_name)
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
        pass
        # json_decode(self.decode_dir_stage1, self.decode_dir_stage2, pool=self.pool)
        # if self.result:
        #     files = os.listdir(self.decode_dir_stage2)
        #     self.assertEqual(len(files), self.result['count_root_files_stage1'], 'count_root_files_stage1')

    def decode_stage3(self):
        decode(self.decode_dir_stage1, self.decode_dir_stage3, pool=self.pool, options=self.options)
        if self.result:
            files = os.listdir(self.decode_dir_stage3)
            self.assertEqual(len(files), self.result['count_root_files_stage3'], 'count_root_files_stage3')

    def decode_stage4(self, descent=None):
        helper.clear_dir(os.path.normpath(self.decode_dir_stage4))
        if not self.index:
            return
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
        if not self.index:
            return
        if descent:
            FileOrganizerCE.pack(self.decode_dir_stage4, self.encode_dir_stage3,
                                 pool=self.pool, index=self.index, descent=descent)
        else:
            FileOrganizer.pack(self.decode_dir_stage4, self.encode_dir_stage3, pool=self.pool, index=self.index)
        if self.result:
            files = os.listdir(self.encode_dir_stage3)
            self.assertEqual(len(files), self.result['count_root_files_stage3'], 'count_root_files_stage3')

    def encode_stage3(self):
        encode(self.decode_dir_stage3, self.encode_dir_stage1, pool=self.pool,
               file_name=os.path.basename(self.src_file), options=self.options)
        self.assert_stage(self.decode_dir_stage1, self.encode_dir_stage1)
        if self.result:
            files = os.listdir(self.encode_dir_stage1)
            self.assertEqual(len(files), self.result['count_root_files_stage1'])

    def encode_stage2(self):
        pass
        # json_encode(self.encode_dir_stage2, self.encode_dir_stage1, pool=self.pool)
        # self.assert_stage(self.decode_dir_stage1, self.encode_dir_stage1)
        # if self.result:
        #     files = os.listdir(self.encode_dir_stage1)
        #     self.assertEqual(len(files), self.result['count_root_files_stage1'])

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
        problems = []
        self._assert_stage(decode_dir, encode_dir, problems, True)
        if problems:
            with open(f'{encode_dir}.txt', 'w', encoding='utf-8') as log:
                for problem in problems:
                    log.write(problem)
        self.assertTrue(not problems, f'files not equal - log in {encode_dir}.txt')

    def _assert_stage(self, decode_dir, encode_dir, problems, root=False):
        entries = os.listdir(decode_dir)
        include_problems = ''
        pbar = None
        if root:
            pbar = tqdm(desc=f'{"Сравниваем с оригиналом":30}', total=len(entries))
        for entry in entries:
            if pbar:
                pbar.update()
            if entry.startswith('configinfo'):
                continue
            path_decode_entry = os.path.join(decode_dir, entry)
            path_encode_entry = os.path.join(encode_dir, entry)
            if os.path.isdir(path_decode_entry):
                self._assert_stage(path_decode_entry, path_encode_entry, problems)
            else:
                try:
                    if entry == 'versions':
                        problem = compare_versions(decode_dir, encode_dir, problems)
                    else:
                        problem = compare_file(path_decode_entry, path_encode_entry, problems)
                except NotEqualLine as err:
                    problem = str(err)
                if problem:
                    problems.append(problem)
        # if problems:
        #     problems = f'   {decode_dir}\n   {encode_dir}{problems}\n'
        # if include_problems:
        #     problems += '\n' + include_problems
        if pbar:
            pbar.close()
        # return pr

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


def compare_file(path_decode_entry, path_encode_entry, problems):
    def ignore():
        len_decode_line = len(decode_line)
        len_encode_line = len(encode_line)
        if decode_line.endswith(b'\r\n'):
            if decode_line[:-2] == encode_line: # Лишние фигурные скобки
                return True
        if not encode_line:
            if decode_line == b'}\r\n' or decode_line == b'}':  # Лишние фигурные скобки
                return True
        if encode_line.endswith(b'\r\n'):
            if decode_line.endswith(b'\r\r\n') and decode_line[:-3] == encode_line[:-2]:
                encode_file.readline()
                # problems += f'\n      {entry:38} {i:6} \\r {decode_line}'
                return True
            if decode_line.endswith(b'\n') and decode_line[:-1] == encode_line[:-2]:
                return True
            if encode_line[:-2] == decode_line:
                return True
            if decode_line.endswith(b'\r\n') \
                    and decode_line[-3] == b','[0] \
                    and (len_decode_line - len_encode_line) == 1:
                return True
        if encode_line.startswith(b'#base64') and encode_line[8:] == decode_line[9:]:
            return True
        if len_decode_line > 36 and len_decode_line == len_encode_line:  # допущение, т.к. в списоке инклюдов порядок теперь разный
            return True
        return False

    problems = ''
    entry = os.path.basename(path_encode_entry)
    folder = os.path.basename(os.path.dirname(path_encode_entry))
    title = os.path.join(folder, entry)

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
                        if ignore():
                            continue
                        problems += f'\n      {title:73} {i:5} {encode_line[:30]}'
                        problems += f'\n      {"":79} {decode_line[:30]}'
                        raise NotEqualLine(problems)
                    elif decode_line.hex() != encode_line.hex():
                        a = 1
                for encode_line in encode_file:
                    i += 1
                    if encode_line == b'}\r\n' or b'}':
                        continue
                    problems += f'\n      {title:73} {i:5} {encode_line[:30]}'
                    raise NotEqualLine(problems)
        except FileNotFoundError:
            problems += f'\n      {title:73}  not encode file'
    return problems


def compare_versions(decode_dir, encode_dir, problems):
    def create_index(versions: list):
        index = []
        count = int((len(versions[0]) - 4) / 2)
        for i in range(count):
            j = i * 2 + 4
            elem = versions[0][j]
            index.append(elem)
        return index

    problems = ''
    decode_data = helper.brace_file_read(decode_dir, 'versions')
    decode_data = create_index(decode_data)
    encode_data = helper.brace_file_read(encode_dir, 'versions')
    encode_data = create_index(encode_data)
    size = len(decode_data)
    for i in range(size):
        j = size - i - 1
        try:
            elem = decode_data[j]
            encode_data.remove(elem)
            decode_data.pop(j)
        except ValueError:
            pass
    if encode_data or decode_data:
        problems += f'\n      {"versions":73} {"":5} {json.dumps(encode_data)}'
        problems += f'\n      {"":79} {json.dumps(decode_data)}'
    return problems
