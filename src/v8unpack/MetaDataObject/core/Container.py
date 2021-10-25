import os

from .. import helper
from ...MetaDataObject import MetaDataObject
from ...ext_exception import ExtException


class Container(MetaDataObject):
    def __init__(self):
        super(Container, self).__init__()
        self.new_dest_path = None
        self.new_dest_dir = None

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
        super(Container, self).decode_object(src_dir, file_name, dest_dir, dest_path, version, header_data)
        self.decode_code(src_dir)
        self.new_dest_path = os.path.join(dest_path, self.header['name'])
        self.new_dest_dir = os.path.join(dest_dir, self.new_dest_path)
        os.makedirs(self.new_dest_dir)

    def write_decode_object(self, dest_dir, dest_path, version):
        helper.json_write(self.header, self.new_dest_dir, f'{self.__class__.__name__}.json')
        self.write_decode_code(self.new_dest_dir, self.__class__.__name__)

    def decode_includes(self, src_dir, dest_dir, dest_path, header_data):
        return super(Container, self).decode_includes(src_dir, dest_dir, self.new_dest_path, header_data)

    def encode_object(self, src_dir, file_name, dest_dir, version):
        self.encode_code(src_dir, self.__class__.__name__)
        return []

    @classmethod
    def encode_get_include_obj(cls, src_dir, dest_dir, include, tasks, version):
        """
        возвращает список задач на парсинг объектов этого типа
        """
        entries = os.listdir(src_dir)
        for entry in entries:
            if os.path.isdir(os.path.join(src_dir, entry)):
                new_src_dir = os.path.join(src_dir, entry)
                tasks.append([include, [new_src_dir, include, dest_dir, version]])
