import os
from base64 import b64encode

from .. import helper
from ..MetaObject import MetaObject
from ..ext_exception import ExtException
from ..metadata_types import MetaDataTypes, MetaDataGroup
from ..version import __version__


class Configuration803(MetaObject):
    ext_code = {
        'seance': 7,
        '803': 6,
        '802': 0,
        'con': 5
    }
    help_file_number = 3

    _images = {
        'Заставка': 2
    }

    _obj_info = {
        '4': '4',
        '9': '9',
        '8': '8',
        'a': 'a',
        'b': 'b',
        'c': 'c',
        'd': 'd',
    }

    def __init__(self, *, obj_name=None, options=None):
        super().__init__(obj_name=obj_name, options=options)
        self.counter = {}

    def decode(self, src_dir, dest_dir, *, version=None, **kwargs):
        self.header = {}
        root = helper.brace_file_read(src_dir, 'root')
        self.header['v8unpack'] = __version__
        self.header["file_uuid"] = root[0][1]
        self.header["root_data"] = root

        _header_data = helper.brace_file_read(src_dir, f'{self.header["file_uuid"]}')
        self.set_header_data(_header_data)

        file_name = self.get_class_name_without_version()

        self.header['version'] = helper.brace_file_read(src_dir, 'version')
        self.header['versions'] = helper.brace_file_read(src_dir, 'versions')
        # shutil.copy2(os.path.join(src_dir, 'versions.json'), os.path.join(dest_dir, 'versions.json'))

        self.decode_code(src_dir)
        self._decode_html_data(src_dir, dest_dir, 'help', header_field='help', file_number=self.help_file_number)
        self._decode_images(src_dir, dest_dir)
        self._decode_info(src_dir, dest_dir, file_name)
        # self._decode_unknown(src_dir, dest_dir, file_name)

        tasks = self.decode_includes(src_dir, dest_dir, '', self.header['data'])

        helper.json_write(self.header, dest_dir, f'{file_name}.json')
        self.write_decode_code(dest_dir, file_name)
        return tasks

    @classmethod
    def get_decode_header(cls, header):
        return header[0][3][1][1][1][1]

    def decode_includes(self, src_dir, dest_dir, dest_path, header_data):
        tasks = []
        index_includes_group = 2
        count_includes_group = int(header_data[0][index_includes_group])
        for index_group in range(count_includes_group):
            group = header_data[0][index_includes_group + index_group + 1]
            group_uuid = group[0]
            group_version = group[1][0]
            try:
                metadata_group = MetaDataGroup(group_uuid)
            except ValueError:
                raise ExtException(message='Неизвестная группа метаданных', detail=group_uuid)
            include = group[1][1] if group_version == '6' else group[1]
            self.decode_include(src_dir, dest_dir, dest_path, tasks, include)
        return tasks

    def encode(self, src_dir, dest_dir, *, file_name=None, include_index=None, file_list=None):
        _file_name = self.get_class_name_without_version()
        self.header = helper.json_read(src_dir, f'{_file_name}.json')
        helper.check_version(__version__, self.header.get('v8unpack', ''))

        if include_index and self.get_options('auto_include'):
            self.fill_header_includes(include_index)  # todo dynamic index

        helper.brace_file_write(self.header["root_data"], dest_dir, 'root')
        file_list.append('root')
        helper.brace_file_write(self.encode_version(), dest_dir, 'version')
        file_list.append('version')
        # shutil.copy2(os.path.join(src_dir, 'versions.json'), os.path.join(dest_dir, 'versions.json'))

        self._encode_html_data(src_dir, 'help', dest_dir, header_field='help', file_number=self.help_file_number)
        self._encode_images(src_dir, dest_dir)
        self.encode_code(src_dir, _file_name)
        self._encode_info(src_dir, _file_name, dest_dir)
        self.write_encode_code(dest_dir)
        helper.brace_file_write(self.header['data'], dest_dir, self.header["file_uuid"])
        file_list.append(self.header["file_uuid"])

        file_list.append('versions')
        file_list.extend(self.file_list)
        helper.brace_file_write(self.encode_versions(file_list), dest_dir, 'versions')
        return None

    def encode_version(self):
        return self.header['version']

    def _decode_images(self, src_dir, dest_dir):
        if self._images:
            for elem in self._images:
                try:
                    data = helper.brace_file_read(src_dir, f'{self.header["uuid"]}.{self._images[elem]}')
                except FileNotFoundError:
                    return
                try:
                    if data[0][2] and data[0][2][0] and data[0][2][0][0]:
                        bin_data = self._extract_b64_data(data[0][2][0])
                        helper.bin_write(bin_data, dest_dir, f'{elem}')
                except IndexError:
                    pass
                self.header[f'image_{elem}'] = data

    def _encode_images(self, src_dir, dest_dir):
        if self._images:
            for elem in self._images:
                try:
                    bin_data = helper.bin_read(src_dir, f'{elem}')
                except FileNotFoundError:
                    bin_data = None
                header = self.header.get(f'image_{elem}')
                if header and len(header[0]) > 1 and bin_data:
                    header[0][2][0][0] += b64encode(bin_data).decode(encoding='utf-8')
                if header:
                    file_name = f'{self.header["uuid"]}.{self._images[elem]}'
                    helper.brace_file_write(header, dest_dir, file_name)
                    self.file_list.append(file_name)

    def fill_header_includes(self, include_index):
        header_data = self.header['data']
        index_includes_group = 2
        count_includes_group = int(header_data[0][index_includes_group])
        for index_group in range(count_includes_group):
            group = header_data[0][index_includes_group + index_group + 1]
            group_uuid = group[0]
            group_version = group[1][0]
            try:
                metadata_group = MetaDataGroup(group_uuid)
            except ValueError:
                raise ExtException(message='Неизвестная группа метаданных', detail=group_uuid)
            include = group[1][1] if group_version == '6' else group[1]
            try:
                count_include_types = int(include[2])
            except IndexError:
                raise ExtException(message='Include types not found', detail=self.__class__.__name__)
            for i in range(count_include_types):
                _metadata = include[i + 3]
                if isinstance(_metadata, str):
                    metadata_type = MetaDataTypes[_metadata]
                    include_objects = include_index.get(_metadata, [])
                    include[i + 3] = [metadata_type.value, str(len(include_objects)), *include_objects]
