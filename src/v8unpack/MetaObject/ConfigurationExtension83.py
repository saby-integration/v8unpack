from ..MetaObject.Configuration83 import Configuration83
from .. import helper


class ConfigurationExtension83(Configuration83):

    def __init__(self):
        super(ConfigurationExtension83, self).__init__()

    @classmethod
    def decode(cls, src_dir, dest_dir):
        self = cls()
        self.header = {}
        root = helper.json_read(src_dir, 'configinfo.json')
        self.header['file_uuid'] = root[1][1]
        self.header['versions'] = root[2]
        self.header['copyinfo'] = root[1]
        self.header['data'] = helper.json_read(src_dir, f'{self.header["file_uuid"]}.json')
        _form_header = self.get_decode_header(self.header['data'])
        helper.decode_header(self.header, _form_header)
        # metadata = self.header['data'][0][4][1]
        helper.json_write(self.header, dest_dir, f'{cls.get_class_name_without_version()}.json')

        tasks = self.decode_includes(src_dir, '', dest_dir, self.header['data'])
        return tasks

    @classmethod
    def encode(cls, src_dir, dest_dir):
        self = cls()
        helper.clear_dir(dest_dir)
        self.header = helper.json_read(src_dir, f'{cls.get_class_name_without_version()}.json')
        root = [
            ["0", self.encode_version()[0][0]],
            self.header['copyinfo'],
            self.header['versions']
        ]
        helper.json_write(root, dest_dir, 'configinfo.json')
        helper.json_write(self.header['data'], dest_dir, f'{self.header["file_uuid"]}.json')
        tasks = self.encode_includes(src_dir, dest_dir)
        return tasks
