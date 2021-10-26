from .. import __version__
from .. import helper
from ..MetaObject import MetaObject


class Configuration803(MetaObject):

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

        self.header['version'] = helper.json_read(src_dir, 'version.json')
        self.header['versions'] = helper.json_read(src_dir, 'versions.json')

        helper.json_write(self.header, dest_dir, f'{cls.get_class_name_without_version()}.json')

        tasks = self.decode_includes(src_dir, dest_dir, '', self.header['data'])
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
    def encode(cls, src_dir, dest_dir, *, version=None, release=None):
        self = cls()
        helper.clear_dir(dest_dir)
        self.header = helper.json_read(src_dir, f'{cls.get_class_name_without_version()}.json')
        helper.check_version(__version__, self.header.get('v8unpack', ''))

        helper.json_write(self.header["root_data"], dest_dir, 'root.json')
        helper.json_write(self.encode_version(), dest_dir, 'version.json')
        helper.json_write(self.header["versions"], dest_dir, 'versions.json')

        helper.json_write(self.header['data'], dest_dir, f'{self.header["file_uuid"]}.json')
        tasks = self.encode_includes(src_dir, dest_dir)
        return tasks

    def encode_version(self):
        return self.header['version']
