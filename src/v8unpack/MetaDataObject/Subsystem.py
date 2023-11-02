from .. import helper
from ..MetaDataObject.core.Container import Container


class Subsystem(Container):
    help_file_number = 0
    ext_code = {}

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super(Subsystem, self).decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        try:
            self.header['info'] = helper.brace_file_read(src_dir, f'{self.header["uuid"]}.1')
        except FileNotFoundError:
            self.header['info'] = None

    def write_encode_object(self, dest_dir):
        super().write_encode_object(dest_dir)
        if self.header['info']:
            file_name = f'{self.header["uuid"]}.1'
            helper.brace_file_write(self.header['info'], dest_dir, file_name)
            self.file_list.append(file_name)
