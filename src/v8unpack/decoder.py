import os
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
    def detect_version(src_dir):
        if os.path.isfile(os.path.join(src_dir, 'root.json')):
            version = helper.json_read(src_dir, 'version.json')
            if version[0][0][0] == "216":
                _tmp = len(version[0][0])
                root = helper.json_read(src_dir, 'root.json')
                header = helper.json_read(src_dir, f'{root[0][1]}.json')
                obj_type = MetaDataTypes(header[0][3][0])
                if _tmp == 2:
                    obj_version = '802'
                elif _tmp == 3:
                    obj_version = version[0][0][2][0][:3]
                    if len(obj_version) == 3:
                        pass
                    elif obj_version == '2':
                        obj_version = '802'
                    else:
                        raise Exception(f'Not supported version {obj_version}')
                else:
                    raise Exception(f'Not supported version {_tmp}')
                try:
                    return available_types[f'{obj_type.name}{obj_version}']
                except KeyError:
                    raise Exception(f'Not supported version {obj_type.name}{obj_version}')
            elif version[0][0][0] == "106":
                return ExternalDataProcessor801()
        if os.path.isfile(os.path.join(src_dir, 'configinfo.json')):
            version = helper.json_read(src_dir, 'configinfo.json')
            if version[0][1][0] == "216":
                if len(version[0][1]) == 3:
                    obj_version = version[0][1][2][0]
                    if obj_version[:3] == '803':
                        return ConfigurationExtension803()
        raise Exception('Не удалось определить парсер')

    @classmethod
    def decode(cls, src_dir, dest_dir, *, pool=None, version=None):
        begin = datetime.now()
        print(f'{"Разбираем объект":30}')
        decoder = cls.detect_version(src_dir)
        helper.clear_dir(dest_dir)
        tasks = decoder.decode(src_dir, dest_dir,
                               version=version)  # возвращает список вложенных объектов MetaDataObject
        while tasks:  # многопоточно рекурсивно декодируем вложенные объекты MetaDataObject
            tasks = helper.run_in_pool(cls.decode_include, tasks, pool, title=f'{"Разбираем вложенные объекты":30}',
                                       need_result=True)
            # tasks = helper.list_merge(*tasks_list)
        print(f'{"Разбор объекта закончен":30}: {datetime.now() - begin}')

    @classmethod
    def decode_include(cls, params):
        include_type, decode_params = params
        try:
            handler = helper.get_class_metadata_object(include_type)
            handler = handler.get_version(decode_params[4])
            tasks = handler.decode(*decode_params, parent_type=include_type)
            return tasks
        except ExtException as err:
            raise ExtException(
                parent=err,
                action=f'{cls.__name__}.decode_include {include_type}'
            )
        except Exception as err:
            raise ExtException(parent=err, action=f'{cls.__name__}.decode_include')

    @classmethod
    def encode(cls, src_dir, dest_dir, *, pool=None, version=None, file_name=None, gui=None, **kwargs):
        begin = datetime.now()
        print(f'{"Собираем объект":30}')
        helper.clear_dir(dest_dir)
        encoder = cls.get_encoder(src_dir, '803' if version is None else version[:3])
        # возвращает список вложенных объектов MetaDataObject
        tasks = encoder.encode(src_dir, dest_dir, version=version, file_name=file_name, gui=gui, **kwargs)

        while tasks:  # многопоточно рекурсивно декодируем вложенные объекты MetaDataObject
            tasks = helper.run_in_pool(cls.encode_include, tasks, pool, title=f'{"Собираем вложенные объекты":30}',
                                       need_result=True)
        print(f'{"Сборка объекта закончена":30}: {datetime.now() - begin}')

    @classmethod
    def get_encoder(cls, src_dir, version='803'):
        if os.path.isfile(os.path.join(src_dir, 'ExternalDataProcessor.json')):
            versions = {
                '801': ExternalDataProcessor801,
                '802': ExternalDataProcessor802,
                '803': ExternalDataProcessor803,
            }
            return versions[version]
        if version == '803':
            if os.path.isfile(os.path.join(src_dir, 'ConfigurationExtension.json')):
                return ConfigurationExtension803
            if os.path.isfile(os.path.join(src_dir, 'Configuration.json')):
                return Configuration803
        elif version == '802':
            if os.path.isfile(os.path.join(src_dir, 'Configuration802.json')):
                return Configuration802
        raise FileNotFoundError(f'Не найдены файлы для сборки версии {version} ({src_dir})')

    @classmethod
    def encode_include(cls, params):
        include_type, encode_params = params
        try:

            handler = helper.get_class_metadata_object(include_type)
            handler = handler.get_version(encode_params[3])
            tasks = handler.encode(*encode_params)
            return tasks
        except Exception as err:
            raise ExtException(parent=err, action=f'Decoder.encode_include({include_type})') from err


def encode(src_dir, dest_dir, *, pool=None, version='803', gui=None, file_name=None, **kwargs):
    Decoder.encode(src_dir, dest_dir, pool=pool, version=version, gui=gui, file_name=file_name, **kwargs)


def decode(src_dir, dest_dir, *, pool=None, version=None):
    Decoder.decode(src_dir, dest_dir, pool=pool, version=version)
