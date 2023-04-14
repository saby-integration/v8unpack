import os

from .. import helper
from ..MetaObject.Configuration803 import Configuration803
from ..version import __version__


class ConfigurationExtension803(Configuration803):
    info = ['6', '8', '9']
    ext_code = {
        'con': '5',
        'app': '6',
        'ssn': '7'
    }

    def __init__(self):
        super(ConfigurationExtension803, self).__init__()

    @classmethod
    def decode(cls, src_dir, dest_dir, *, version=None):
        self = cls()
        self.header = {}
        root = helper.brace_file_read(src_dir, 'configinfo')
        self.header['v8unpack'] = __version__
        self.header['file_uuid'] = root[1][1]
        self.header['version'] = root[0][1]
        # self.header['versions'] = root[2]
        self.header['copyinfo'] = root[1]
        # self.header['copyinfo'][2] = b64decode(self.header['copyinfo'][2])[:-16].hex()
        self.header['data'] = helper.brace_file_read(src_dir, f'{self.header["file_uuid"]}')
        _form_header = self.get_decode_header(self.header['data'])
        helper.decode_header(self.header, _form_header)
        product_version = self.header['data'][0][3][1][1][15]
        if version is None:
            self.header['compatibility_version'] = self.header['data'][0][3][1][1][43]
        else:
            self.header['compatibility_version'] = version
            self.header['data'][0][3][1][1][43] = version

        self.decode_code(src_dir)

        for i in self.info:  # хз что это
            file_name = f'{self.header["uuid"]}.{i}'
            if os.path.isdir(os.path.join(src_dir, file_name)):
                continue
            try:
                self.header[f'info{i}'] = helper.brace_file_read(src_dir, file_name)
            except FileNotFoundError:
                pass
        tasks = self.decode_includes(src_dir, dest_dir, '', self.header['data'])

        helper.txt_write(helper.str_decode(product_version), dest_dir, 'version.bin', encoding='utf-8')
        helper.json_write(self.header, dest_dir, f'{cls.get_class_name_without_version()}.json')
        self.write_decode_code(dest_dir, cls.__name__)

        return tasks

    def encode(self, src_dir, dest_dir, *, version=None, file_name=None, gui=None, include_index=None, file_list=None,
               **kwargs):
        self.header = helper.json_read(src_dir, f'{self.get_class_name_without_version()}.json')

        self.set_product_info(src_dir, file_name)

        if version is not None:
            self.header['data'][0][3][1][1][43] = version
        if gui is not None:
            self.header['data'][0][3][1][1][38] = gui

        helper.check_version(__version__, self.header.get('v8unpack', ''))

        if include_index:
            self.fill_header_includes(include_index)

        # self.header['copyinfo'][2] = b64encode(bytes.fromhex(self.header['copyinfo'][2]+md5().digest().hex())).decode()
        root = [
            ["0", self.encode_version()],
            self.header['copyinfo'],
            # self.header['versions']
            ["____versions____"]
        ]
        self.encode_code(src_dir, self.__class__.__name__)
        self.write_encode_code(dest_dir)
        helper.brace_file_write(root, dest_dir, 'configinfo')
        helper.brace_file_write(self.header['data'], dest_dir, self.header["file_uuid"])
        for i in self.info:  # хз что это
            try:
                helper.brace_file_write(self.header[f'info{i}'], dest_dir, f'{self.header["uuid"]}.{i}')
            except KeyError:
                pass

        return None

    def set_product_version(self, product_version):
        self.header['data'][0][3][1][1][15] = helper.str_encode(product_version)
