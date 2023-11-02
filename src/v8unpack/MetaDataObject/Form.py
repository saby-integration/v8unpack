import os

from ..MetaDataObject.core.Simple import SimpleNameFolder
from ..MetaDataObject.versions.Form801 import Form801
from ..MetaDataObject.versions.Form802 import Form802
from ..MetaDataObject.versions.Form803 import Form803
from ..MetaDataObject.versions.OldForm803 import OldForm801, OldForm803
from ..ext_exception import ExtException


class Form(SimpleNameFolder):
    versions = {
        '801': Form801,
        '802': Form802,
        '803': Form803,
        '5-5': OldForm801,
        '7-7': OldForm801,
        '9-9': OldForm803,
        '12-12': OldForm803,
        '13-13': OldForm803,
        '0-5': Form801,
        '0-7': Form801,
        '0-9': Form803,
        '0-12': Form803,
        '0-13': Form803,
        '1-9': Form803,
        '1-12': Form803,
        '1-13': Form803
    }
    form_version_index = {
        "0": 3,
        "1": 4,
        "5": 2,
        "7": 2,
        "9": 2,
        "12": 2,
        "13": 2,
    }

    @classmethod
    def decode_get_handler(cls, src_dir, file_name, options):
        obj_version, form_version = cls.get_form_version(src_dir, file_name)
        handler = cls.get_version(f'{obj_version}-{form_version}')(options=options)
        handler.obj_version = obj_version
        return handler

    @classmethod
    def get_form_version(cls, path, file_name):
        try:
            _path = os.path.join(path, file_name)
            with open(_path, 'r', encoding='utf-8-sig') as file:
                header = file.read(20)
                root = header.split('{')

                obj_type_version, x = root[2].split(',')
                form_version, x = root[cls.form_version_index[obj_type_version]].split(',')
                return obj_type_version, form_version
        except Exception as err:
            raise ExtException(message="Неудалось опеределить версию формы", detail=f'{cls.__name__} {file_name}')
