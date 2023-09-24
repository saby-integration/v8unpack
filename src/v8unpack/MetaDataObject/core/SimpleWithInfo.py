from .Simple import Simple
from .. import helper


class SimpleWithInfo(Simple):
    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super(Simple, self).decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        try:
            self.header['info'] = helper.json_read(src_dir, f'{self.header["uuid"]}.0.json')
        except FileNotFoundError:
            return

    def write_encode_object(self, dest_dir):
        super(Simple, self).write_encode_object(dest_dir)
        info = self.header.get('info')
        if info:
            helper.json_write(info, dest_dir, f'{self.header["uuid"]}.0.json')
