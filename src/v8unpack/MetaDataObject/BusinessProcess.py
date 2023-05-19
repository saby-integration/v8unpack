from ..MetaDataObject.core.Container import Container
from .. import helper


class BusinessProcess(Container):
    ext_code = {
        'obj': 6,
        'mgr': 8
    }
    help_file_number = 5
    pass

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super().decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        try:
            package = helper.bin_read(src_dir, f'{self.header["uuid"]}.7')
            helper.bin_write(package, self.new_dest_dir, 'Карта маршрута.bin')
        except FileNotFoundError:
            return

    def encode_object(self, src_dir, file_name, dest_dir):
        res = super().encode_object(src_dir, file_name, dest_dir)
        try:
            package = helper.bin_read(src_dir, 'Карта маршрута.bin')
            file_name = f'{self.header["uuid"]}.7'
            helper.bin_write(package, dest_dir, file_name)
            self.file_list.append(file_name)
        except FileNotFoundError:
            return
        return res