import json
import os

from .helper import remove_descent_from_filename
from .ext_exception import ExtException


def get(index: dict, path: str, file_name: str):
    try:
        _index = index
        if path:
            _path = path.split('\\')
            for _dir in _path:
                _index = _index[_dir]
        return _index[file_name]
    except TypeError:
        raise ExtException(
            message="Ошибка c уровнями вложенности в Index.json",
            detail=f'{path}\{file_name}',
            action='index.get'
        )


def update_index(src_dir: str, index_file_name: str, dest_dir: str):
    def _update_index(_src_dir, _index, _dest_dir, _path):
        entries = os.listdir(os.path.join(_src_dir, _path))
        for entry in entries:
            entry = remove_descent_from_filename(entry)
            new_path = os.path.join(_path, entry)
            if os.path.isdir(os.path.join(_src_dir, new_path)):
                if entry not in _index:
                    _index[entry] = {}
                _update_index(_src_dir, _index[entry], _dest_dir, new_path)
            else:
                if entry not in _index:
                    _index[entry] = os.path.join(_dest_dir, _path, entry) if _dest_dir else ''
        pass

    try:
        with open(index_file_name, 'r', encoding='utf-8') as f:
            index = json.load(f)
    except FileNotFoundError:
        index = {}

    _update_index(src_dir, index, dest_dir, '')
    with open(index_file_name, 'w+', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
