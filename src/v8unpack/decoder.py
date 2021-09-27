from .import helper
from .MetaObject.ExternalDataProcessor81 import ExternalDataProcessor81
from .MetaObject.ExternalDataProcessor82 import ExternalDataProcessor82
from .MetaObject.ExternalDataProcessor83 import ExternalDataProcessor83
from .MetaObject.ConfigurationExtension83 import ConfigurationExtension83
from .MetaObject.Configuration83 import Configuration83
import os


class Decoder:
    @staticmethod
    def detect_version(src_dir):
        if os.path.isfile(os.path.join(src_dir, 'root.json')):
            # пока не понятно на сколько надежно, возможно нужно читать файл заголовка
            version = helper.json_read(src_dir, 'version.json')
            if version[0][0][0] == "216":
                _tmp = len(version[0][0])
                if _tmp == 2:
                    return ExternalDataProcessor82()
                if _tmp == 3 and version[0][0][2][0] == '80314':
                    return ExternalDataProcessor83()
                if _tmp == 3 and version[0][0][2][0] == '80315':  # todo не надежно, но найти анализировать uuid типа
                    return Configuration83()
            elif version[0][0][0] == "106":
                return ExternalDataProcessor81()
        if os.path.isfile(os.path.join(src_dir, 'configinfo.json')):
            version = helper.json_read(src_dir, 'configinfo.json')
            if version[0][1][0] == "216":
                if len(version[0][1]) == 3 and version[0][1][2][0] in ['80314', '80315']:  # todo понять в чем отличия
                    return ConfigurationExtension83()
        raise Exception('Не удалось опеределить парсер')

    @classmethod
    def decode(cls, src_dir, dest_dir, *, pool=None):
        decoder = cls.detect_version(src_dir)
        helper.clear_dir(dest_dir)
        tasks = decoder.decode(src_dir, dest_dir)  # возвращает список вложенных объектов MetaDataObject
        while tasks:  # многопоточно рекурсивно декодируем вложенные объекты MetaDataObject
            tasks_list = helper.run_in_pool(cls.decode_include, tasks, pool)
            tasks = helper.list_merge(*tasks_list)

    @classmethod
    def decode_include(cls, include_type, decode_params):
        try:
            handler = helper.get_class(f'v8unpack.MetaDataObject.{include_type}.{include_type}')
            handler = handler.get_version(decode_params[4])
            tasks = handler.decode(*decode_params)
            return tasks
        except Exception as err:
            raise err.__class__(err.args[0], include_type) from err

    @classmethod
    def encode(cls, src_dir, dest_dir, *, pool=None, version='83'):
        helper.clear_dir(dest_dir)
        encoder = cls.get_encoder(src_dir, version)
        tasks = encoder.encode(src_dir, dest_dir)  # возвращает список вложенных объектов MetaDataObject
        while tasks:  # многопоточно рекурсивно декодируем вложенные объекты MetaDataObject
            tasks_list = helper.run_in_pool(cls.encode_include, tasks, pool)
            tasks = helper.list_merge(*tasks_list)

    @classmethod
    def get_encoder(cls, src_dir, version):
        if os.path.isfile(os.path.join(src_dir, 'ExternalDataProcessor.json')):
            versions = {
                '81': ExternalDataProcessor81,
                '82': ExternalDataProcessor82,
                '83': ExternalDataProcessor83,
            }
            return versions[version]
        if version == '83':
            if os.path.isfile(os.path.join(src_dir, 'ConfigurationExtension.json')):
                return ConfigurationExtension83
            if os.path.isfile(os.path.join(src_dir, 'Configuration.json')):
                return Configuration83
        raise FileNotFoundError(f'Не найдены файлы для сборки версии {version} ({src_dir})')

    @classmethod
    def encode_include(cls, include_type, encode_params):
        try:
            handler = helper.get_class(f'v8unpack.MetaDataObject.{include_type}.{include_type}')
            handler = handler.get_version(encode_params[3])
            tasks = handler.encode(*encode_params)
            return tasks
        except Exception as err:
            raise err.__class__(err.args[0], include_type) from err


def encode(src_dir, dest_dir, *, pool=None, version='83'):
    Decoder.encode(src_dir, dest_dir, pool=pool, version=version)


def decode(src_dir, dest_dir, *, pool=None):
    Decoder.decode(src_dir, dest_dir, pool=pool)
