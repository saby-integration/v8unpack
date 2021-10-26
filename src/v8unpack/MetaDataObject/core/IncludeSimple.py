from ...MetaDataObject import MetaDataObject
from ...ext_exception import ExtException


class IncludeSimple(MetaDataObject):
    ext_code = {'obj': 2}

    def __init__(self):
        super(IncludeSimple, self).__init__()
        self.new_dest_path = None
        self.new_dest_dir = None

    @classmethod
    def decode(cls, src_dir, file_name, dest_dir, dest_path, version):
        raise Exception('Так быть не должно, этот класс обслуживает вложенные объекты')

    @classmethod
    def decode_local_include(cls, parent, header_data, src_dir, dest_dir, dest_path, version):
        try:
            self = cls()
            self.version = version
            self.set_header_data(header_data)
            self.decode_code(src_dir)
            self.write_decode_object(dest_dir, dest_path, version)
        except Exception as err:
            raise ExtException(
                parent=err,
                action=f'{cls.__name__}.decode_local_include'
            ) from err

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][3][2][9]

    def encode_object(self, src_dir, file_name, dest_dir, version):
        self.encode_code(src_dir, self.header["name"])
        return []

    def write_encode_object(self, dest_dir):
        self.write_encode_code(dest_dir)
