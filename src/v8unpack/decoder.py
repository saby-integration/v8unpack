import os
import shutil
from datetime import datetime

from . import helper
from .MetaObject.Configuration802 import Configuration802
from .MetaObject.Configuration803 import Configuration803
from .MetaObject.ConfigurationExtension803 import ConfigurationExtension803
from .MetaObject.ExternalDataProcessor801 import ExternalDataProcessor801
from .MetaObject.ExternalDataProcessor802 import ExternalDataProcessor802
from .MetaObject.ExternalDataProcessor803 import ExternalDataProcessor803
from .ext_exception import ExtException
from .metadata_types import MetaDataTypes

available_types = {
    'ExternalDataProcessor801': ExternalDataProcessor801,
    'ExternalDataProcessor802': ExternalDataProcessor802,
    'ExternalDataProcessor803': ExternalDataProcessor803,
    'Configuration802': Configuration802,
    'Configuration803': Configuration803
}


class Decoder:
    @staticmethod
    def detect_version(src_dir, options=None):
        def init_handler(handler):
            handler_version = handler.version
            if options:
                _version = options.get('version')
                if _version and _version.startswith(handler_version):
                    handler_version = _version
            options['version'] = handler_version
            return handler(options=options)

        if os.path.isfile(os.path.join(src_dir, 'root')):
            version = helper.brace_file_read(src_dir, 'version')
            if int(version[0][0][0]) >= 216:
                _tmp = len(version[0][0])
                root = helper.brace_file_read(src_dir, 'root')
                header = helper.brace_file_read(src_dir, root[0][1])
                obj_type = MetaDataTypes(header[0][3][0])
                if _tmp == 2:
                    obj_version = '802'
                elif _tmp == 3:
                    obj_version = version[0][0][2][0][:3]
                    if len(obj_version) == 3:
                        pass
                    elif obj_version in ['1', '2']:
                        obj_version = '802'
                    else:
                        raise Exception(f'Not supported version {obj_version}')
                else:
                    raise Exception(f'Not supported version {_tmp}')
                try:
                    return init_handler(available_types[f'{obj_type.name}{obj_version}'])
                except KeyError:
                    raise Exception(f'Not supported version {obj_type.name}{obj_version}')
            elif version[0][0][0] == "106":
                return init_handler(ExternalDataProcessor801)
        if os.path.isfile(os.path.join(src_dir, 'configinfo')):
            version = helper.brace_file_read(src_dir, 'configinfo')
            if version[0][1][0] == "216":
                if len(version[0][1]) == 3:
                    obj_version = version[0][1][2][0]
                    if obj_version[:3] == '803':
                        return init_handler(ConfigurationExtension803)
        raise Exception('Не удалось определить парсер')

    @classmethod
    def decode(cls, src_dir, dest_dir, *, pool=None, options=None):
        begin = datetime.now()
        print(f'{"Разбираем объект":30}')
        decoder = cls.detect_version(src_dir, options=options)
        helper.clear_dir(dest_dir)
        tasks = decoder.decode(src_dir, dest_dir)  # возвращает список вложенных объектов MetaDataObject
        while tasks:  # многопоточно рекурсивно декодируем вложенные объекты MetaDataObject
            tasks = helper.run_in_pool(cls.decode_include, tasks, pool, title=f'{"Разбираем вложенные объекты":30}',
                                       need_result=True)
            # tasks = helper.list_merge(*tasks_list)
        print(f'{"Разбор объекта закончен":30}: {datetime.now() - begin}')

    @classmethod
    def decode_include(cls, params):
        include_type, (obj_uuid, src_dir, dest_dir, new_dest_path, options) = params
        try:
            handler = helper.get_class_metadata_object(include_type)
            # handler = handler.get_version(decode_params[4])
            tasks = handler.decode(obj_uuid, src_dir, dest_dir, new_dest_path, options, parent_type=include_type)
            return tasks
        except ExtException as err:
            raise ExtException(
                parent=err,
                action=f'{cls.__name__}.decode_include {include_type}'
            )
        except Exception as err:
            raise ExtException(parent=err, action=f'{cls.__name__}.decode_include')

    @classmethod
    def encode(cls, src_dir, dest_dir, *, pool=None, file_name=None, options=None):
        begin = datetime.now()
        print(f'{"Собираем объект":30}')
        helper.clear_dir(dest_dir)
        encoder = cls.get_encoder(src_dir, options)
        # возвращает список вложенных объектов MetaDataObject
        helper.clear_dir(dest_dir)

        parent_id = encoder.get_class_name_without_version()
        child_tasks = encoder.encode_includes(src_dir, file_name, dest_dir, encoder.version, parent_id)
        include_index = {}
        file_list = []
        object_task = []
        title = f'{"Собираем вложенные объекты":30}'
        while object_task or child_tasks:  # многопоточно рекурсивно декодируем вложенные объекты MetaDataObject
            _file_list, _include_index, _object_task, child_tasks = helper.run_in_pool_encode_include(
                cls.encode_include, child_tasks, pool,
                title=title
            )
            if _file_list:
                file_list.extend(_file_list)
            if _include_index:
                helper.update_dict(include_index, _include_index)
            if _object_task:
                object_task.append(_object_task)
            if not child_tasks and object_task:
                _object_task = object_task.pop()
                for elem in _object_task:
                    elem[1][5] = include_index.pop(f"{elem[1][4]}/{elem[0]}/{elem[1][1]}")
                child_tasks = _object_task
                title = f'{"Собираем составные объекты":30}'
            a = 1

        encoder.encode(src_dir, dest_dir, file_name=file_name, include_index=include_index.pop(parent_id, None),
                       file_list=file_list)

        print(f'{"Сборка объекта закончена":30}: {datetime.now() - begin}')

    @classmethod
    def get_encoder(cls, src_dir, options=None):
        version = '803'
        version = options.get('version', version) if options else version
        if os.path.isfile(os.path.join(src_dir, 'ExternalDataProcessor.json')):
            versions = {
                '801': ExternalDataProcessor801,
                '802': ExternalDataProcessor802,
                '803': ExternalDataProcessor803,
            }
            return versions[version](options=options)
        if version == '803':
            if os.path.isfile(os.path.join(src_dir, 'ConfigurationExtension.json')):
                return ConfigurationExtension803(options=options)
            if os.path.isfile(os.path.join(src_dir, 'Configuration.json')):
                return Configuration803(options=options)
        elif version == '802':
            if os.path.isfile(os.path.join(src_dir, 'Configuration802.json')):
                return Configuration802(options=options)
        raise FileNotFoundError(f'Не найдены файлы для сборки версии {version} ({src_dir})')

    @classmethod
    def encode_include(cls, params):
        include_type, encode_params = params
        try:

            handler = helper.get_class_metadata_object(include_type)
            handler = handler.get_version(encode_params[3])()
            handler.title = include_type
            object_task, child_tasks = handler.encode(*encode_params)
            return object_task, child_tasks
        except Exception as err:
            raise ExtException(parent=err, action=f'Decoder.encode_include({include_type})') from err


def encode(src_dir, dest_dir, *, pool=None, options=None, file_name=None):
    def unpack_dummy():
        version = options.get('version')
        helper.clear_dir(dest_dir)
        dummy_path = os.path.join(src_dir, 'dummy.zip')
        if version and int(version.ljust(5, '0')) >= 80316 and os.path.isfile(dummy_path):
            helper.clear_dir(container_dest_dir)
            shutil.unpack_archive(dummy_path, container_dest_dir)
            return os.path.join(dest_dir, '1')
        return container_dest_dir

    if not options:
        options = {}
    if not options.get('version'):
        options['version'] = '803'

    container_dest_dir = os.path.join(dest_dir, '0')
    container_dest_dir = unpack_dummy()
    Decoder.encode(src_dir, container_dest_dir, pool=pool, options=options, file_name=file_name)


def decode(src_dir, dest_dir, *, pool=None, options=None):
    containers = os.listdir(src_dir)
    containers_count = len(containers)
    if containers_count not in [1, 2]:
        raise NotImplementedError(f'Количество контейнеров {containers_count}')

    _src_dir = os.path.join(src_dir, containers[-1])
    Decoder.decode(_src_dir, dest_dir, pool=pool, options=options)
    if containers_count == 2:
        shutil.make_archive(os.path.join(dest_dir, 'dummy'), 'zip', os.path.join(src_dir, '0'))
