import os
import shutil
from datetime import datetime

from . import helper
from .MetaObject.Configuration import Configuration
from .MetaObject.ConfigurationExtension import ConfigurationExtension
from .MetaObject.ExternalDataProcessor import ExternalDataProcessor
from .ext_exception import ExtException
from .metadata_types import MetaDataTypes

available_types = {
    'ExternalDataProcessor': ExternalDataProcessor,
    'Configuration': Configuration,
    'ConfigurationExtension': ConfigurationExtension
}


class Decoder:
    @staticmethod
    def get_handler_by_version_file(*, version=None, root=None, header=None, options=None, configinfo=None, **kwargs):
        if root:
            if int(version[0][0][0]) >= 216:
                _tmp = len(version[0][0])
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
                    # if not options.get('version'):
                    options['obj_version'] = obj_version
                    return available_types[obj_type.name](options=options, obj_version=options['obj_version'])
                except KeyError:
                    raise Exception(f'Not supported type {obj_type.name}')
            elif version[0][0][0] == "106":
                options['obj_version'] = '801'
                return ExternalDataProcessor(options=options, obj_version=options['obj_version'])
        if configinfo:
            if int(configinfo[0][1][0]) >= 216:
                if len(configinfo[0][1]) == 3:
                    obj_version = configinfo[0][1][2][0]
                    if obj_version.startswith('803'):
                        options['obj_version'] = obj_version
                        return ConfigurationExtension(options=options, obj_version=options['obj_version'])
        raise Exception('Не удалось определить парсер')

    @classmethod
    def detect_version(cls, src_dir, options=None):
        version = None
        root = None
        header = None
        configinfo = None
        if os.path.isfile(os.path.join(src_dir, 'root')):
            version = helper.brace_file_read(src_dir, 'version')
            root = helper.brace_file_read(src_dir, 'root')
            header = helper.brace_file_read(src_dir, root[0][1])
        if os.path.isfile(os.path.join(src_dir, 'configinfo')):
            configinfo = helper.brace_file_read(src_dir, 'configinfo')

        return cls.get_handler_by_version_file(
            version=version,
            root=root,
            header=header,
            options=options,
            configinfo=configinfo
        )

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
        _type = cls.get_encoder(src_dir, options)
        header = helper.json_read(src_dir, f'{_type}.json')
        encoder = cls.get_handler_by_version_file(options=options, **header)
        encoder.header = header

        # возвращает список вложенных объектов MetaDataObject
        helper.clear_dir(dest_dir)

        parent_id = encoder.get_class_name_without_version()
        child_tasks = encoder.encode_includes(src_dir, file_name, dest_dir, parent_id)
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
                title = f'{"Собираем вложенные объекты":30}'
            a = 1

        encoder.encode(src_dir, dest_dir, file_name=file_name, include_index=include_index.pop(parent_id, None),
                       file_list=file_list)

        print(f'{"Сборка объекта закончена":30}: {datetime.now() - begin}')

    @classmethod
    def get_encoder(cls, src_dir, options=None):
        _type = None
        for _type in available_types:
            if os.path.isfile(os.path.join(src_dir, f'{_type}.json')):
                return _type
        raise FileNotFoundError(f'Не найдены файлы для сборки версии ({src_dir})')

    @classmethod
    def encode_include(cls, params):
        include_type, (new_src_dir, entry, dest_dir, options, parent_id, include_index) = params
        try:
            handler = helper.get_class_metadata_object(include_type)

            # handler = handler.get_version(options.get('version', '803')[:3])(options=options)
            # handler.title = include_type
            object_task, child_tasks = handler.encode(new_src_dir, entry, dest_dir, parent_id, include_index,
                                                      options=options)
            return object_task, child_tasks
        except Exception as err:
            raise ExtException(parent=err, action=f'Decoder.encode_include({include_type})') from err


def encode(src_dir, dest_dir, *, pool=None, options=None, file_name=None):
    def unpack_dummy():
        helper.clear_dir(dest_dir)
        dummy_path = os.path.join(src_dir, 'dummy.zip')
        if os.path.isfile(dummy_path):
            helper.clear_dir(container_dest_dir)
            shutil.unpack_archive(dummy_path, container_dest_dir)
            return os.path.join(dest_dir, '1')
        return container_dest_dir

    try:
        product_version = helper.txt_read(src_dir, 'version.bin', encoding='utf-8')
        options['product_version'] = product_version
    except FileNotFoundError:
        pass

    container_dest_dir = os.path.join(dest_dir, '0')
    container_dest_dir = unpack_dummy()
    # options = helper.set_options_param(options, 'version', version[:3])
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
