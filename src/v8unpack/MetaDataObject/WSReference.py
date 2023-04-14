import os
import shutil

from ..MetaDataObject.core.Simple import Simple


class WSReference(Simple):
    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][2]

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super().decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)

        src = os.path.join(src_dir, f'{self.header["uuid"]}.0')
        dest = os.path.join(dest_dir, dest_path, self.header["name"])
        if not os.path.isdir(src):
            return
        shutil.copytree(src, dest)

    def encode_object(self, src_dir, file_name, dest_dir, version):
        super().encode_object(src_dir, file_name, dest_dir, version)

        src = os.path.join(src_dir, self.header["name"])
        if not os.path.isdir(src):
            return
        dir_name = f'{self.header["uuid"]}.0'
        dest = os.path.join(dest_dir, dir_name)
        shutil.copytree(src, dest)
        self.file_list.append(dir_name)
