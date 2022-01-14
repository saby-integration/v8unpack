from ...MetaDataObject import MetaDataObject


class Simple(MetaDataObject):
    def __init__(self):
        super().__init__()

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super().decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        self.decode_code(src_dir)

    def write_decode_object(self, dest_dir, dest_path, version):
        super(Simple, self).write_decode_object(dest_dir, dest_path, version)

    def decode_includes(self, src_dir, dest_dir, dest_path, header):
        return []

    def encode_includes(self, src_dir, dest_dir):
        return []

    def encode_object(self, src_dir, file_name, dest_dir, version):
        self.encode_code(src_dir, self.header["name"])
        return []
