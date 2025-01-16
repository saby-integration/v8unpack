from ..MetaDataObject.core.Container import Container
from ..ext_exception import ExtException
from .. import helper


class ExchangePlan(Container):
    ext_code = {'obj': 2, 'mgr': 3}
    help_file_number = 0
    pass

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][12]

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super().decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        try:
            self.header['info'] = helper.brace_file_read(src_dir, f'{self.header["uuid"]}.1')
        except FileNotFoundError:
            self.header['info'] = None

    def write_encode_object(self, dest_dir):
        try:
            super().write_encode_object(dest_dir)
            if self.header['info']:
                file_name = f'{self.header["uuid"]}.1'
                helper.brace_file_write(self.header['info'], dest_dir, file_name)
                self.file_list.append(file_name)
        except Exception as err:
            raise ExtException(parent=err,
                               detail=f'{self.__class__.__name__} {self.header["name"]} {self.header["uuid"]}')
