from .Simple import Simple
from .. import helper
import os
import shutil


class SimpleWithInfo(Simple):
    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super(Simple, self).decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        try:
            _src = os.path.join(src_dir, f'{self.header["uuid"]}.0')
            _dest = os.path.join(dest_dir, self.new_dest_path, f'{self.new_dest_file_name}.0.c1brace')
            shutil.copy2(_src, _dest)
            # self.header['info'] = helper.brace_file_read(src_dir, f'{self.header["uuid"]}.0')
        except FileNotFoundError:
            return

    # def write_encode_object(self, dest_dir):
    #     super().write_encode_object(dest_dir)
        # info = self.header.get('info')
        # if info:
        #     file_name = f'{self.header["uuid"]}.0'
        #     helper.brace_file_write(info, dest_dir, file_name)
        #     self.file_list.append(file_name)

    def encode_object(self, src_dir, file_name, dest_dir, version):
        super().encode_object(src_dir, file_name, dest_dir, version)
        try:
            _src = os.path.join(src_dir, f'{file_name}.0.c1brace')
            _dest_file_name = f'{self.header["uuid"]}.0'
            _dest = os.path.join(dest_dir, _dest_file_name)
            shutil.copy2(_src, _dest)
            self.file_list.append(_dest_file_name)
            # self.header['info'] = helper.brace_file_read(src_dir, f'{self.header["uuid"]}.0')
        except FileNotFoundError:
            return
