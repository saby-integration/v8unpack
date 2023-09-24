from ..MetaDataObject import MetaDataObject
import os
from .. import helper


class XDTOPackage(MetaDataObject):

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super().decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        try:
            package = helper.bin_read(src_dir, f'{self.header["uuid"]}.0.bin')
            helper.bin_write(package, self.new_dest_dir, f'{self.new_dest_file_name}.bin')
        except FileNotFoundError:
            return

    def decode_includes(self, src_dir, dest_dir, dest_path, header):
        return []

    def encode_includes(self, src_dir, file_name, dest_dir, version):
        return []

    def encode_object(self, src_dir, file_name, dest_dir, version):
        try:
            package = helper.bin_read(src_dir, f'{file_name}.bin')
            helper.bin_write(package, dest_dir, f'{self.header["uuid"]}.0.bin')
        except FileNotFoundError:
            return
        return []
