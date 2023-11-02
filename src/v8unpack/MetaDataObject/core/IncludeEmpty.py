from ...MetaDataObject import MetaDataObject


class IncludeEmpty(MetaDataObject):

    @classmethod
    def decode(cls, src_dir, file_name, dest_dir, dest_path, version, parent_type=None):
        raise Exception('Так быть не должно, этот класс обслуживает вложенные объекты')

    @classmethod
    def decode_local_include(cls, parent, header_data, src_dir, dest_dir, dest_path, version):
        return

    def encode_object(self, src_dir, file_name, dest_dir):
        raise Exception('Так быть не должно, этот класс обслуживает вложенные объекты')
