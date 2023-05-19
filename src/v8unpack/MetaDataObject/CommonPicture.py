import os
from base64 import b64decode, b64encode

from .. import helper
from ..MetaDataObject.core.Simple import Simple
from ..ext_exception import ExtException


class CommonPicture(Simple):
    def __init__(self, *, obj_name=None, options=None):
        super().__init__(obj_name=obj_name, options=options)
        self.ext_code = {}
        self.data = None
        self.raw_data = None

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        try:
            super().decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
            try:
                self.header['info'] = helper.brace_file_read(src_dir, f'{self.header["uuid"]}.0')
            except FileNotFoundError:
                return
            if self.header['info'][0][2] and self.header['info'][0][2][0] and self.header['info'][0][2][0][0]:
                bin_data = self._extract_b64_data(self.header['info'][0][2][0])

                extension = helper.get_extension_from_comment(self.header['comment'])
                _dest_dir = os.path.join(dest_dir, dest_path)
                if dest_dir:
                    helper.bin_write(bin_data, _dest_dir, f'{self.header["name"]}.{extension}')
        except Exception as err:
            raise ExtException(parent=err)

    def encode_object(self, src_dir, file_name, dest_dir):
        super().encode_object(src_dir, file_name, dest_dir)

        extension = helper.get_extension_from_comment(self.header['comment'])
        try:
            bin_data = helper.bin_read(src_dir, f'{self.header["name"]}.{extension}')
            self.header['info'][0][2][0][0] += b64encode(bin_data).decode(encoding='utf-8')
            file_name = f'{self.header["uuid"]}.0'
            helper.brace_file_write(self.header['info'], dest_dir, file_name)
            self.file_list.append(file_name)
        except FileNotFoundError:
            pass
