from ...MetaDataObject import MetaDataObject
from ...ext_exception import ExtException


class IncludeSimple(MetaDataObject):
    ext_code = {'obj': 2}

    def __init__(self, *, obj_name=None, options=None):
        super().__init__(obj_name=obj_name, options=options)
        self.new_dest_path = None
        self.new_dest_dir = None

    @classmethod
    def decode(cls, src_dir, file_name, dest_dir, dest_path, version, parent_type=None):
        raise Exception('Так быть не должно, этот класс обслуживает вложенные объекты')

    @classmethod
    def decode_local_include(cls, parent, header_data, src_dir, dest_dir, dest_path, options):
        try:
            self = cls(options=options)
            self.set_header_data(header_data)
            self.set_write_decode_mode(dest_dir, dest_path)
            self.decode_code(src_dir)
            self.write_decode_object(dest_dir, self.new_dest_path, self.new_dest_file_name)
        except Exception as err:
            raise ExtException(
                parent=err,
                action=f'{cls.__name__}.decode_local_include'
            ) from err

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][3][2][9]

    def encode_object(self, src_dir, file_name, dest_dir):
        self.encode_code(src_dir, self.header["name"])
        return []

    def get_include_obj_uuid(self):
        return self.header['data']

    def write_encode_object(self, dest_dir):
        self.write_encode_code(dest_dir)

