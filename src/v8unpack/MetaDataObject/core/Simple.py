from ...MetaDataObject import MetaDataObject


class Simple(MetaDataObject):

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        super().decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        if self.help_file_number is not None:
            self._decode_html_data(src_dir, self.new_dest_dir, self.new_dest_file_name, header_field='help',
                                   file_number=self.help_file_number)
        self.decode_code(src_dir)

    def decode_includes(self, src_dir, dest_dir, dest_path, header):
        return []

    def encode_includes(self, src_dir, file_name, dest_dir, version):
        return []

    def encode_object(self, src_dir, file_name, dest_dir, version):
        if self.help_file_number is not None:
            self._encode_html_data(src_dir, file_name, dest_dir, header_field='help', file_number=self.help_file_number)
        self.encode_code(src_dir, file_name)
        return []


class SimpleNameFolder(Simple):
    def set_write_decode_mode(self, dest_dir, dest_path):
        self.set_mode_decode_in_name_folder(dest_dir, dest_path)

    @classmethod
    def encode_get_include_obj(cls, src_dir, dest_dir, include, tasks, version):
        cls.encode_get_include_obj_from_named_folder(src_dir, dest_dir, include, tasks, version)

    @classmethod
    def get_encode_file_name(cls, file_name):
        return cls.get_obj_name()
