from .Simple import Simple
from .. import helper


class SimpleWithInfo(Simple):
    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super(Simple, self).decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        try:
            self.header['info'] = helper.brace_file_read(src_dir, f'{self.header["uuid"]}.0')
        except FileNotFoundError:
            return

    def write_encode_object(self, dest_dir):
        super(Simple, self).write_encode_object(dest_dir)
        info = self.header.get('info')
        if info:
            file_name = f'{self.header["uuid"]}.0'
            helper.brace_file_write(info, dest_dir, file_name)
            self.file_list.append(file_name)
