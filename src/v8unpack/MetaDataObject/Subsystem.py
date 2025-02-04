from .. import helper
from ..ext_exception import ExtException
from ..MetaDataObject.core.Container import Container


class Subsystem(Container):
    help_file_number = 0
    ext_code = {}

    # todo Subsystem не учтено в старых конфакх может быть папка 0 c image и info

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super(Subsystem, self).decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        try:
            self.header['info'] = helper.brace_file_read(src_dir, f'{self.header["uuid"]}.1')
        except FileNotFoundError:
            self.header['info'] = None
            return
        pass

    def write_encode_object(self, dest_dir):
        super().write_encode_object(dest_dir)
        try:
            if self.header['info']:
                file_name = f'{self.header["uuid"]}.1'
                helper.brace_file_write(self.header['info'], dest_dir, file_name)
                self.file_list.append(file_name)
        except Exception as err:
            raise ExtException(parent=err,
                               detail=f'{self.__class__.__name__} {self.header["name"]} {self.header["uuid"]}')
