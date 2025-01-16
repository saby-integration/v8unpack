import os

from .. import helper
from ..MetaObject import MetaObject
from ..ext_exception import ExtException


class MetaDataObject(MetaObject):
    versions = None
    help_file_number = None

    def __init__(self, *, meta_obj_class=None, obj_version=None, options=None):
        super().__init__(meta_obj_class=meta_obj_class, obj_version=obj_version, options=options)
        self.path = ''
        self.new_dest_path = None
        self.new_dest_dir = None
        self.new_dest_file_name = None

    def get_obj_name(self):
        return self.meta_obj_class.__name__ if self.meta_obj_class else self.__class__.__name__

    @classmethod
    def get_version(cls, header_data, option):
        if cls.versions is None:
            return cls
        return header_data[0][1][0]

    @staticmethod
    def brace_file_read(src_dir, file_name):
        return helper.brace_file_read(src_dir, file_name)

    @classmethod
    def get_handler(cls, header_data, options):
        try:
            # version = helper.get_options_param(options, 'version', '803')
            if cls.versions is None:
                return cls(options=options, obj_version=options['version'])
            obj_version = cls.get_version(header_data, options)
            try:
                return cls.versions[obj_version](options=options, meta_obj_class=cls, obj_version=obj_version)
            except KeyError:
                raise Exception(f'Нет реализации {cls.__name__} для версии "{obj_version}"')
        except Exception as err:
            raise ExtException(message='Не смогли получить класс объекта', detail=f'{cls.__name__} {err}')

    @classmethod
    def decode(cls, src_dir: str, file_name: str, dest_dir: str, dest_path: str, options, *, parent_type=None):
        try:
            header_data = cls.brace_file_read(src_dir, file_name)
            self = cls.get_handler(header_data, options)
            # self = cls()
            # if parent_type:
            #     self.title = parent_type
            self.decode_header(header_data)
            self.decode_object(src_dir, file_name, dest_dir, dest_path, self.obj_version, header_data)
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

    def decode_object(self, src_dir, file_name, dest_dir, dest_path, version, header_data):
        self.set_write_decode_mode(dest_dir, dest_path)

    def write_decode_object(self, dest_dir, dest_path, file_name):
        try:
            dest_full_path = os.path.join(dest_dir, dest_path)

            id_data = {
                'uuid': self.header.pop('uuid'),
                'name': self.header.pop('name')
            }
            self.header['obj_version'] = self.obj_version
            helper.json_write(id_data, dest_full_path, f'{file_name}.id.json')
            helper.json_write(self.header, dest_full_path, f'{file_name}.json')
            self.write_decode_code(dest_full_path, file_name)
        except Exception as err:
            raise ExtException(parent=err)

    # def set_mode_decode_in_name_folder(self, dest_dir, dest_path):
    #     self.new_dest_path = os.path.join(dest_path, self.header['name'])
    #     self.new_dest_dir = os.path.join(dest_dir, self.new_dest_path)
    #     self.new_dest_file_name = self.get_obj_name()
    #     helper.makedirs(self.new_dest_dir)

    # def set_mode_decode_in_root_folder(self, dest_dir, dest_path):
    #     self.new_dest_path = dest_path
    #     self.new_dest_dir = os.path.join(dest_dir, self.new_dest_path)
    #     self.new_dest_file_name = self.header['name']

    def get_internal_data(self):
        return self.uuid

    @classmethod
    def read_header(cls, src_dir, src_file_name, data_id):
        header = helper.json_read(src_dir, f'{src_file_name}.json')
        header['name'] = data_id['name']
        header['uuid'] = data_id['uuid']
        return header

    @classmethod
    def encode(cls, src_dir, file_name, dest_dir, parent_id, include_index, options):
        # src_file_name = self.get_encode_file_name(file_name)
        src_file_name = cls.__name__
        try:
            # header_data = header['header']
            # self = cls.get_handler(header_data, options)
            if not include_index:
                self = cls(options=options)
                current_obj_id = f"{parent_id}/{cls.__name__}/{file_name}"
                child_tasks = self.encode_includes(src_dir, src_file_name, dest_dir, current_obj_id)
                if child_tasks:
                    object_task = [self.__class__.__name__, [src_dir, file_name, dest_dir, options, parent_id, {}]]
                    return object_task, child_tasks
            try:
                data_id = helper.json_read(src_dir, f'{src_file_name}.id.json')
                header = cls.read_header(src_dir, src_file_name, data_id)
            except FileNotFoundError:
                return None, None
            self = cls.get_handler(header['header'], options)
            self.header = header
        except Exception as err:
            raise ExtException(
                parent=err,
                dump=dict(src_dir=src_dir, file_name=file_name),
                action=f'{cls.__name__}.encode') from err

        try:
            self.name = data_id['name']
            self.uuid = data_id['uuid']
            self.obj_version = self.header['obj_version']
            if include_index:
                self.fill_header_includes(include_index)  # todo dynamic index
            self.encode_object(src_dir, src_file_name, dest_dir)
            self.write_encode_object(dest_dir)
            return dict(
                parent_id=parent_id,
                file_list=self.file_list,
                obj_type=self.get_obj_name(),
                obj_name=self.name,
                obj_uuid=self.uuid,
                obj_data=self.get_internal_data()
            ), None
        except Exception as err:
            raise ExtException(
                parent=err,
                dump=dict(uuid=self.header['uuid'], src_dir=src_dir, file_name=file_name),
                action=f'{self.__class__.__name__}.encode') from err

    def encode_object(self, src_dir, file_name, dest_dir):
        msg = f'Нет реализации для "{self.__class__.__name__}"'
        raise Exception(msg)

    def write_encode_object(self, dest_dir):
        try:
            file_name = f'{self.header["uuid"]}'
            self.encode_header()
            helper.brace_file_write(self.header['header'], dest_dir, file_name)
            self.file_list.append(file_name)
            self.write_encode_code(dest_dir)
        except Exception as err:
            raise ExtException(parent=err,
                               detail=f'{self.__class__.__name__} {self.header["name"]} {self.header["uuid"]}')

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

    def set_write_decode_mode(self, dest_dir, dest_path):
        self.new_dest_path = os.path.join(dest_path, self.header['name'])
        self.new_dest_dir = os.path.join(dest_dir, self.new_dest_path)
        self.new_dest_file_name = self.get_obj_name()
        helper.makedirs(self.new_dest_dir)
        # self.set_mode_decode_in_name_folder(dest_dir, dest_path)

    # def set_write_decode_mode(self, dest_dir, dest_path):
    #     self.set_mode_decode_in_name_folder(dest_dir, dest_path)
    # self.set_mode_decode_in_root_folder(dest_dir, dest_path)

    # def get_encode_file_name(self, file_name):
    #     return self.get_obj_name()

    # def get_encode_file_name(self, file_name):
    #     return file_name
