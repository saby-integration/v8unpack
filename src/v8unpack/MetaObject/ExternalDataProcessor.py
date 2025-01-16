from ..version import __version__
from .. import helper
from ..MetaObject import MetaObject
from ..ext_exception import ExtException


class ExternalDataProcessor(MetaObject):

    def __init__(self, *, meta_obj_class=None, obj_version=None, options=None):
        super().__init__(meta_obj_class=meta_obj_class, obj_version=obj_version, options=options)
        self.data = None

    def decode(self, src_dir, dest_dir):
        self.header = {}
        self.data = {}
        root = helper.brace_file_read(src_dir, 'root')
        self.header['root'] = True
        self.header["file_uuid"] = root[0][1]
        _header_data = helper.brace_file_read(src_dir, f'{self.header["file_uuid"]}')
        self.decode_header(_header_data, id_in_separate_file=False)

        root = helper.brace_file_read(src_dir, 'root')
        self.header['v8unpack'] = __version__
        self.header['file_uuid'] = root[0][1]
        self.header['version'] = helper.brace_file_read(src_dir, 'version')
        # self.header['versions'] = helper.brace_file_read(src_dir, 'versions')
        self.header['copyinfo'] = helper.brace_file_read(src_dir, 'copyinfo')

        try:
            form1 = helper.brace_file_read(src_dir, f'{self.header["uuid"]}.1')
        except FileNotFoundError:
            form1 = None

        self.data['form1'] = form1

        self.decode_code(src_dir)
        pass
        _file_name = self.get_class_name_without_version()

        tasks = self.decode_includes(src_dir, dest_dir, '', self.header['header'])

        self.header['obj_version'] = self.obj_version
        helper.json_write(self.header, dest_dir, f'{_file_name}.json')
        helper.json_write(self.data, dest_dir, f'{_file_name}.data{self.obj_version}.json')
        self.write_decode_code(dest_dir, 'ExternalDataProcessor')

        return tasks
        # helper.run_in_pool(self.decode_include, tasks, pool)
        pass

    @classmethod
    def get_decode_includes(cls, header_data):
        return [header_data[0][3][1]]

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][3][1][1][3][1]

    def encode(self, src_dir, dest_dir, *, file_name=None, include_index=None, file_list=None, **kwargs):
        try:
            _file_name = self.get_class_name_without_version()
            self.header = helper.json_read(src_dir, f'{_file_name}.json')
            helper.check_version(__version__, self.header.get('v8unpack', ''))
            try:
                self.data = helper.json_read(src_dir, f'{_file_name}.data{self.obj_version}.json')
            except FileNotFoundError:
                self.data = self.encode_empty_data()

            self.set_product_info(src_dir, file_name)

            if include_index and self.get_options('auto_include'):
                self.fill_header_includes(include_index)

            helper.brace_file_write(self.encode_root(), dest_dir, 'root')
            file_list.append('root')
            helper.brace_file_write(self.header['version'], dest_dir, 'version')
            file_list.append('version')
            helper.brace_file_write(self.header['copyinfo'], dest_dir, 'copyinfo')
            file_list.append('copyinfo')
            # helper.brace_file_write(self.header['versions'], dest_dir, 'versions')
            helper.brace_file_write(self.header['header'], dest_dir, self.header["file_uuid"])
            file_list.append(self.header["file_uuid"])
            if self.data.get('form1'):
                file_name = f'{self.header["uuid"]}.1'
                helper.brace_file_write(self.data['form1'], dest_dir, file_name)
                file_list.append(file_name)
            self.encode_code(src_dir, 'ExternalDataProcessor')
            self.write_encode_code(dest_dir)

            file_list.append('versions')
            file_list.extend(self.file_list)
            versions = self.encode_versions(file_list)
            helper.brace_file_write(versions, dest_dir, 'versions')
            return None
        except Exception as err:
            raise ExtException(parent=err)

    def encode_root(self):
        return [[
            "2",
            self.header["file_uuid"],
            ""
        ]]

    def encode_empty_data(self):
        return {
            "copyinfo": [
                [
                    "4",
                    [
                        "0"
                    ],
                    [
                        "0"
                    ],
                    [
                        "0"
                    ],
                    [
                        "0",
                        "0"
                    ],
                    [
                        "0"
                    ]
                ]
            ]
        }
