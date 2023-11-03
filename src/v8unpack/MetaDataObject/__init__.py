import os

from .. import helper
from ..MetaObject import MetaObject
from ..ext_exception import ExtException


class MetaDataObject(MetaObject):
    versions = None
    version = None
    help_file_number = None

    def __init__(self, *, obj_name=None, options=None):
        super().__init__(obj_name=obj_name, options=options)
        self.path = ''
        self.new_dest_path = None
        self.new_dest_dir = None
        self.new_dest_file_name = None
        self.obj_version = None

    @classmethod
    def get_obj_name(cls):
        return cls._obj_name if cls._obj_name else cls.__name__

    @classmethod
    def get_version(cls, version):
        if cls.versions is None:
            return cls
        try:
            return cls.versions[version]
        except KeyError:
            raise Exception(f'Нет реализации {cls.__name__} для версии "{version}"')

    @staticmethod
    def brace_file_read(src_dir, file_name):
        return helper.brace_file_read(src_dir, file_name)

    @classmethod
    def decode_get_handler(cls, src_dir, file_name, options):
        try:
            version = helper.get_options_param(options, 'version', '803')
            return cls.get_version(version)(options=options)
        except Exception as err:
            raise ExtException(message='Не смогли получить класс объекта', detail=f'{cls.__name__} {err}')

    @classmethod
    def decode(cls, src_dir: str, file_name: str, dest_dir: str, dest_path: str, options, *, parent_type=None):
        try:
            self = cls.decode_get_handler(src_dir, file_name, options)
            header_data = cls.brace_file_read(src_dir, file_name)
            # self = cls()
            if parent_type:
                self.title = parent_type
            self.decode_object(src_dir, file_name, dest_dir, dest_path, self.version, header_data)
            tasks = self.decode_includes(src_dir, dest_dir, self.new_dest_path, header_data)
            self.write_decode_object(dest_dir, self.new_dest_path, self.new_dest_file_name)
            return tasks
        except Exception as err:
            problem_file = os.path.join(os.path.basename(src_dir), file_name)
            raise ExtException(
                parent=err,
                message="Ошибка декодирования",
                detail=f'"{cls.__name__}" файл "{problem_file}" ({dest_path})',
                action=f'{cls.__name__}.decode'
            ) from err

    def set_write_decode_mode(self, dest_dir, dest_path):
        self.set_mode_decode_in_root_folder(dest_dir, dest_path)

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        self.set_header_data(header_data)
        self.set_write_decode_mode(dest_dir, dest_path)

    def write_decode_object(self, dest_dir, dest_path, file_name):
        dest_full_path = os.path.join(dest_dir, dest_path)
        helper.json_write(self.header, dest_full_path, f'{file_name}.json')
        self.write_decode_code(dest_full_path, file_name)

    def set_mode_decode_in_name_folder(self, dest_dir, dest_path):
        self.new_dest_path = os.path.join(dest_path, self.header['name'])
        self.new_dest_dir = os.path.join(dest_dir, self.new_dest_path)
        self.new_dest_file_name = self.get_obj_name()
        helper.makedirs(self.new_dest_dir)

    def set_mode_decode_in_root_folder(self, dest_dir, dest_path):
        self.new_dest_path = dest_path
        self.new_dest_dir = os.path.join(dest_dir, self.new_dest_path)
        self.new_dest_file_name = self.header['name']

    def get_include_obj_uuid(self):
        return self.header['uuid']

    def encode(self, src_dir, file_name, dest_dir, parent_id, include_index):
        src_file_name = self.get_encode_file_name(file_name)
        try:
            if not include_index:
                current_obj_id = f"{parent_id}/{self.title}/{file_name}"
                child_tasks = self.encode_includes(src_dir, src_file_name, dest_dir, current_obj_id)
                if child_tasks:
                    object_task = [self.__class__.__name__, [src_dir, file_name, dest_dir, self.options, parent_id, {}]]
                    return object_task, child_tasks
            try:
                self.header = helper.json_read(src_dir, f'{src_file_name}.json')
            except FileNotFoundError:
                return
            if include_index and self.get_options('auto_include'):
                self.fill_header_includes(include_index)  # todo dynamic index
            self.encode_object(src_dir, src_file_name, dest_dir)
            self.write_encode_object(dest_dir)
            return dict(
                parent_id=parent_id,
                file_list=self.file_list,
                obj_type=self.title,
                obj_uuid=self.get_include_obj_uuid()
            ), None
        except Exception as err:
            raise ExtException(
                parent=err,
                dump=dict(uuid=self.header['uuid'], src_dir=src_dir, file_name=file_name),
                action=f'{self.__class__.__name__}.encode') from err

    def get_encode_file_name(self, file_name):
        return file_name

    def encode_object(self, src_dir, file_name, dest_dir):
        msg = f'Нет реализации для "{self.__class__.__name__}"'
        raise Exception(msg)

    def write_encode_object(self, dest_dir):
        file_name = f'{self.header["uuid"]}'
        helper.brace_file_write(self.header['data'], dest_dir, file_name)
        self.file_list.append(file_name)
        self.write_encode_code(dest_dir)

    @staticmethod
    def get_metadata_object_version(path, file_name):
        _path = os.path.join(path, file_name)
        with open(_path, 'r', encoding='utf-8-sig') as file:
            header = file.read(9)
            root = header.split('{')
            if len(root) < 3 or root[1][0] != '1':
                raise ExtException(message='Неизвестная версия объекта метаданных',
                                   detail=file_name)
            root = root[2].split(',')
            return int(root[0])
