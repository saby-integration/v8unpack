from ...MetaDataObject import MetaDataObject


class IncludeEmpty(MetaDataObject):

    @classmethod
    def decode(cls, src_dir: str, file_name: str, dest_dir: str, dest_path: str, options, *, parent_type=None,
               parent_container_uuid=None):
        raise Exception('Так быть не должно, этот класс обслуживает вложенные объекты')

    @classmethod
    def decode_internal_include(cls, parent, header_data, src_dir, dest_dir, dest_path, version):
        return

    def encode_object(self, src_dir, file_name, dest_dir):
        raise Exception('Так быть не должно, этот класс обслуживает вложенные объекты')
