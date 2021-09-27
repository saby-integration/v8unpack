import os
from ..MetaObject import MetaObject
from .. import helper


class ExternalDataProcessor(MetaObject):

    def __init__(self):
        super(ExternalDataProcessor, self).__init__()
        self.code = None
        self.data = None

    @classmethod
    def decode(cls, src_dir, dest_dir):
        self = cls()
        self.header = {}
        self.data = {}
        root = helper.json_read(src_dir, 'root.json')
        self.header["file_uuid"] = root[0][1]
        _header_data = helper.json_read(src_dir, f'{self.header["file_uuid"]}.json')
        self.set_header_data(_header_data)

        root = helper.json_read(src_dir, 'root.json')
        self.header['file_uuid'] = root[0][1]
        self.header['versions'] = helper.json_read(src_dir, 'versions.json')
        self.data['copyinfo'] = helper.json_read(src_dir, 'copyinfo.json')

        self.decode_code(src_dir)
        pass
        _file_name = self.get_class_name_without_version()
        helper.json_write(self.header, dest_dir, f'{_file_name}.json')
        helper.json_write(self.data, dest_dir, f'{_file_name}.data{self.version}.json')
        if self.code:
            helper.txt_write(self.code, dest_dir, f'{_file_name}.1c')

        tasks = self.decode_includes(src_dir, dest_dir, '', self.header['data'])
        return tasks
        # helper.run_in_pool(self.decode_include, tasks, pool)
        pass

    @classmethod
    def get_decode_includes(cls, header_data):
        return [header_data[0][3][1]]

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][3][1][1][3][1]

    def decode_code(self, src_dir):
        _code_dir = f'{os.path.join(src_dir, self.header["uuid"])}.0'
        if os.path.isdir(_code_dir):
            self.header['info'] = helper.json_read(_code_dir, 'info.json')
            self.code = self.read_raw_code(_code_dir, 'text.txt')

    @classmethod
    def encode(cls, src_dir, dest_dir, *, pool=None):
        self = cls()
        helper.clear_dir(dest_dir)
        _file_name = self.get_class_name_without_version()
        self.header = helper.json_read(src_dir, f'{_file_name}.json')
        self.data = helper.json_read(src_dir, f'{_file_name}.data{self.version}.json')
        helper.json_write(self.encode_root(), dest_dir, 'root.json')
        helper.json_write(self.encode_version(), dest_dir, 'version.json')
        helper.json_write(self.header['versions'], dest_dir, 'versions.json')
        helper.json_write(self.data['copyinfo'], dest_dir, 'copyinfo.json')
        helper.json_write(self.header['data'], dest_dir, f'{self.header["file_uuid"]}.json')
        if self.header.get('info'):
            _code_dir = f'{os.path.join(dest_dir, self.header["uuid"])}.0'
            os.mkdir(_code_dir)
            helper.json_write(self.header['info'], _code_dir, 'info.json')
            self.code = helper.txt_read(src_dir, f'{_file_name}.1c')
            self.write_raw_code(self.code, _code_dir, 'text.txt')
        tasks = self.encode_includes(src_dir, dest_dir)
        return tasks

    def encode_root(self):
        return [[
            "2",
            self.header["file_uuid"],
            ""
        ]]

