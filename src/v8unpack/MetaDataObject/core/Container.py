from ...MetaDataObject import MetaDataObject
from ...ext_exception import ExtException


class Container(MetaDataObject):

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][1]

    @classmethod
    def get_decode_includes(cls, header_data):
        try:
            return [header_data[0]]
        except IndexError:
            raise ExtException(msg='Include types not found', detail=cls.__name__)

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super().decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        self.decode_code(src_dir)

    def set_write_decode_mode(self, dest_dir, dest_path):
        self.set_mode_decode_in_name_folder(dest_dir, dest_path)

    def encode_object(self, src_dir, file_name, dest_dir, version):
        self.encode_code(src_dir, self.__class__.__name__)
        return []

    @classmethod
    def encode_get_include_obj(cls, src_dir, dest_dir, include, tasks, version):
        cls.encode_get_include_obj_from_named_folder(src_dir, dest_dir, include, tasks, version)

    @classmethod
    def get_encode_file_name(cls, file_name):
        return cls.get_obj_name()
