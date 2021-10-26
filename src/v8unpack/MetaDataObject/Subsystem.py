from .. import helper
from ..MetaDataObject.core.Container import Container


class Subsystem(Container):
    pass

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super(Subsystem, self).decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        try:
            self.header['info'] = helper.json_read(src_dir, f'{self.header["uuid"]}.1.json')
        except FileNotFoundError:
            self.header['info'] = None

    def write_encode_object(self, dest_dir):
        super(Subsystem, self).write_encode_object(dest_dir)
        if self.header['info']:
            helper.json_write(self.header['info'], dest_dir, f'{self.header["uuid"]}.1.json')
