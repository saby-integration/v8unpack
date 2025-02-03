import os

from .. import helper
from ..ext_exception import ExtException
from ..MetaObject.Configuration import Configuration
from ..version import __version__


class ConfigurationExtension(Configuration):
    info = ['6', '8', '9']
    ext_code = {
        'con': '5',
        'app': '6',
        'ssn': '7'
    }
    _obj_info = {
        'a': 'a',
    }

    def decode(self, src_dir, dest_dir, *, version=None, **kwargs):
        self.header = {}
        root = helper.brace_file_read(src_dir, 'configinfo')
        self.header['configinfo'] = root
        self.header['v8unpack'] = __version__
        self.header['file_uuid'] = root[1][1]
        self.header['version'] = root[0][1]
        # self.header['versions'] = root[2]
        self.header['copyinfo'] = root[1]
        # self.header['copyinfo'][2] = b64decode(self.header['copyinfo'][2])[:-16].hex()
        self.header['header'] = helper.brace_file_read(src_dir, f'{self.header["file_uuid"]}')
        _form_header = self.get_decode_header(self.header['header'])
        helper.decode_header(self, _form_header, id_in_separate_file=False)
        product_version = self.header['header'][0][3][1][1][15]
        if version is None:
            self.header['compatibility_version'] = self.header['header'][0][3][1][1][43]
        else:
            self.header['compatibility_version'] = version
            self.header['header'][0][3][1][1][43] = version

        self.decode_code(src_dir)

        for i in self.info:  # хз что это
            file_name = f'{self.header["uuid"]}.{i}'
            if os.path.isdir(os.path.join(src_dir, file_name)):
                continue
            try:
                self.header[f'info{i}'] = helper.brace_file_read(src_dir, file_name)
            except FileNotFoundError:
                pass
        file_name = self.get_class_name_without_version()
        self._decode_info(src_dir, dest_dir, file_name)
        tasks = self.decode_includes(src_dir, dest_dir, '', self.header['header'])

        helper.txt_write(helper.str_decode(product_version), dest_dir, 'version.bin', encoding='utf-8')
        self.header['obj_version'] = self.obj_version
        helper.json_write(self.header, dest_dir, f'{self.get_class_name_without_version()}.json')
        self.write_decode_code(dest_dir, self.__class__.__name__)

        return tasks

    def encode(self, src_dir, dest_dir, *, file_name=None, include_index=None, file_list=None):
        try:
            self.header = helper.json_read(src_dir, f'{self.get_class_name_without_version()}.json')

            self.set_product_info(src_dir, file_name)

            # установка режима совместимости
            version = self.get_options('version')
            if version is not None:
                self.header['header'][0][3][1][1][43] = version
            prefix = self.get_options('prefix')
            if prefix is not None:
                self.header['header'][0][3][1][1][42] = helper.str_encode(prefix)

            # gui = self.get_options('gui')
            # if gui is not None:
            #     self.header['header'][0][3][1][1][38] = gui

            helper.check_version(__version__, self.header.get('v8unpack', ''))

            if include_index and self.get_options('auto_include'):
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
            _file_name = self.get_class_name_without_version()
            self._encode_info(src_dir, _file_name, dest_dir)
            helper.brace_file_write(root, dest_dir, 'configinfo')
            helper.brace_file_write(self.header['header'], dest_dir, self.header["file_uuid"])
            for i in self.info:  # хз что это
                try:
                    helper.brace_file_write(self.header[f'info{i}'], dest_dir, f'{self.header["uuid"]}.{i}')
                except KeyError:
                    pass

            return None
        except Exception as err:
            raise ExtException(parent=err)


