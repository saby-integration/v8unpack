from ... import helper
from ...MetaDataObject import MetaDataObject
from ...ext_exception import ExtException


class Container(MetaDataObject):
    predefined_file_number = None

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
        if self.help_file_number is not None:
            self._decode_html_data(src_dir, self.new_dest_dir, self.new_dest_file_name, header_field='help',
                                   file_number=self.help_file_number)
        if self.predefined_file_number is not None:
            self._decode_predefined(src_dir, self.new_dest_dir)
        self.decode_code(src_dir)

    def _decode_predefined(self, src_dir, dest_dir):
        try:
            data = helper.bin_read(src_dir, f'{self.header["uuid"]}.{self.predefined_file_number}.json')
            helper.bin_write(data, dest_dir, 'Предустановленные данные.json')
        except FileNotFoundError:
            return

    def set_write_decode_mode(self, dest_dir, dest_path):
        self.set_mode_decode_in_name_folder(dest_dir, dest_path)

    def encode_object(self, src_dir, file_name, dest_dir, version):
        if self.help_file_number is not None:
            self._encode_html_data(src_dir, file_name, dest_dir, header_field='help', file_number=self.help_file_number)
        if self.predefined_file_number is not None:
            self._encode_predefined(src_dir, dest_dir)
        self.encode_code(src_dir, self.__class__.__name__)
        return []

    def _encode_predefined(self, src_dir, dest_dir):
        try:
            package = helper.bin_read(src_dir, 'Предустановленные данные.json')
            helper.bin_write(package, dest_dir, f'{self.header["uuid"]}.{self.predefined_file_number}.json')
        except FileNotFoundError:
            return

    @classmethod
    def encode_get_include_obj(cls, src_dir, dest_dir, include, tasks, version):
        cls.encode_get_include_obj_from_named_folder(src_dir, dest_dir, include, tasks, version)

    @classmethod
    def get_encode_file_name(cls, file_name):
        return cls.get_obj_name()
