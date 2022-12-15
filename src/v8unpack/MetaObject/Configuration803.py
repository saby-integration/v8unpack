import os
import shutil
from base64 import b64encode

from ..version import __version__
from .. import helper
from ..MetaObject import MetaObject


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

    def __init__(self):
        super(Configuration803, self).__init__()
        self.counter = {}

    @classmethod
    def decode(cls, src_dir, dest_dir, *, version=None):
        self = cls()
        self.header = {}
        root = helper.json_read(src_dir, 'root.json')
        self.header['v8unpack'] = __version__
        self.header["file_uuid"] = root[0][1]
        self.header["root_data"] = root

        _header_data = helper.json_read(src_dir, f'{self.header["file_uuid"]}.json')
        self.set_header_data(_header_data)

        file_name = cls.get_class_name_without_version()

        self.header['version'] = helper.json_read(src_dir, 'version.json')
        # self.header['versions'] = helper.json_read(src_dir, 'versions.json')
        shutil.copy2(os.path.join(src_dir, 'versions.json'), os.path.join(dest_dir, 'versions.json'))

        self.decode_code(src_dir)
        self._decode_html_data(src_dir, dest_dir, 'help', header_field='help', file_number=self.help_file_number)
        self._decode_images(src_dir, dest_dir)
        self._decode_info(src_dir, dest_dir, file_name)

        helper.json_write(self.header, dest_dir, f'{file_name}.json')

        tasks = self.decode_includes(src_dir, dest_dir, '', self.header['data'])
        self.write_decode_code(dest_dir, file_name)
        return tasks
        pass

    @classmethod
    def get_decode_header(cls, header):
        return header[0][3][1][1][1][1]

    @classmethod
    def get_decode_includes(cls, header_data):
        return [
            header_data[0][3][1],
            header_data[0][4][1][1],
            header_data[0][5][1],
            header_data[0][6][1],
            header_data[0][7][1],
            header_data[0][8][1],
        ]

    @classmethod
    def encode(cls, src_dir, dest_dir, *, version=None, file_name=None, **kwargs):
        self = cls()
        helper.clear_dir(dest_dir)
        file_name = cls.get_class_name_without_version()
        self.header = helper.json_read(src_dir, f'{file_name}.json')
        helper.check_version(__version__, self.header.get('v8unpack', ''))

        helper.json_write(self.header["root_data"], dest_dir, 'root.json')
        helper.json_write(self.encode_version(), dest_dir, 'version.json')
        # helper.json_write(self.header["versions"], dest_dir, 'versions.json')
        shutil.copy2(os.path.join(src_dir, 'versions.json'), os.path.join(dest_dir, 'versions.json'))

        self._encode_html_data(src_dir, 'help', dest_dir, header_field='help', file_number=self.help_file_number)
        self._encode_images(src_dir, dest_dir)
        self.encode_code(src_dir, file_name)
        self._encode_info(src_dir, file_name, dest_dir)
        self.write_encode_code(dest_dir)
        helper.json_write(self.header['data'], dest_dir, f'{self.header["file_uuid"]}.json')
        tasks = self.encode_includes(src_dir, file_name, dest_dir, version)
        return tasks

    def encode_version(self):
        return self.header['version']

    def _decode_images(self, src_dir, dest_dir):
        if self._images:
            for elem in self._images:
                try:
                    data = helper.json_read(src_dir, f'{self.header["uuid"]}.{self._images[elem]}.json')
                except FileNotFoundError:
                    return
                try:
                    if data[0][2] and data[0][2][0] and data[0][2][0][0]:
                        bin_data = self._extract_b64_data(data[0][2][0])
                        helper.bin_write(bin_data, dest_dir, f'{elem}.bin')
                except IndexError:
                    pass
                self.header[f'image_{elem}'] = data

    def _encode_images(self, src_dir, dest_dir):
        if self._images:
            for elem in self._images:
                try:
                    bin_data = helper.bin_read(src_dir, f'{elem}.bin')
                except FileNotFoundError:
                    bin_data = None
                header = self.header.get(f'image_{elem}')
                if header and len(header[0]) > 1 and bin_data:
                    header[0][2][0][0] += b64encode(bin_data).decode(encoding='utf-8')
                if header:
                    helper.json_write(header, dest_dir, f'{self.header["uuid"]}.{self._images[elem]}.json')
