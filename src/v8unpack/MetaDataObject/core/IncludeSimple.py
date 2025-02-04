from ...MetaDataObject import MetaDataObject
from ...ext_exception import ExtException


class IncludeSimple(MetaDataObject):
    ext_code = {'obj': 2}

    def __init__(self, *, meta_obj_class=None, obj_version=None, options=None):
        super().__init__(meta_obj_class=meta_obj_class, obj_version=obj_version, options=options)
        self.new_dest_path = None
        self.new_dest_dir = None

    @classmethod
    def decode(cls, src_dir, file_name, dest_dir, dest_path, version, parent_type=None):
        raise Exception('Так быть не должно, этот класс обслуживает вложенные объекты')

    @classmethod
    def decode_internal_include(cls, parent, header_data, src_dir, dest_dir, dest_path, options):
        try:
            self = cls(options=options)
            self.decode_header(header_data)
            self.set_write_decode_mode(dest_dir, dest_path)
            self.decode_code(src_dir)
            self.write_decode_object(dest_dir, self.new_dest_path, self.new_dest_file_name)
            return self.uuid
        except Exception as err:
            raise ExtException(
                parent=err,
                action=f'{cls.__name__}.decode_internal_include'
            ) from err

    @classmethod
    def get_decode_header(cls, header_data):
        return header_data[0][1][3][2][9]

    def encode_object(self, src_dir, file_name, dest_dir):
        self.encode_code(src_dir, self.__class__.__name__)
        return []

    def get_internal_data(self):
        return self.header['header']

    def write_encode_object(self, dest_dir):
        self.encode_header()
        self.write_encode_code(dest_dir)

