import os
from base64 import b64decode, b64encode

from .. import helper
from ..MetaDataObject.core.Simple import Simple
from ..ext_exception import ExtException


class CommonPicture(Simple):
    def __init__(self):
        super(Simple, self).__init__()
        self.data = None
        self.raw_data = None

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        try:
            super(CommonPicture, self).decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
            try:
                self.raw_data = helper.json_read(src_dir, f'{self.header["uuid"]}.0.json')
            except FileNotFoundError:
                return
            if self.raw_data[0][2] and self.raw_data[0][2][0][0]:
                self.data = b64decode(self.raw_data[0][2][0][0][8:])
                extension = helper.get_extension_from_comment(self.header['comment'])
                _dest_dir = os.path.join(dest_dir, dest_path)
                if dest_dir:
                    helper.bin_write(self.data, _dest_dir, f'{self.header["name"]}.{extension}')
        except Exception as err:
            raise ExtException(parent=err)

    def encode_object(self, src_dir, file_name, dest_dir, version):
        super(CommonPicture, self).encode_object(src_dir, file_name, dest_dir, version)

        extension = helper.get_extension_from_comment(self.header['comment'])
        try:
            bin_data = helper.bin_read(src_dir, f'{self.header["name"]}.{extension}')
            self.raw_data = [
                [
                    "1",
                    [
                        "0",
                        "0",
                        "-1",
                        "-1"
                    ],
                    [
                        [
                            "#base64:" + b64encode(bin_data).decode(encoding='utf-8')
                        ]
                    ]
                ]
            ]
            helper.json_write(self.raw_data, dest_dir, f'{self.header["uuid"]}.0.json')
        except FileNotFoundError:
            pass
