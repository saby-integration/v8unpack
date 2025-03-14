import json
import os

from .helper import remove_descent_from_filename
from .ext_exception import ExtException
from . import helper


def get_from_index(index: dict, path: str, file_name: str):
    try:
        _index = index
        if path:
            _path = os.path.normpath(path)
            _path = path.split(os.sep)
            for _dir in _path:
                _index = _index[_dir]
        try:
            return _index[file_name]
        except KeyError:
            return os.path.join(_index['*'], file_name)
    except TypeError:
        raise ExtException(
            message="Ошибка c уровнями вложенности в Index.json",
            detail=f'{path}/{file_name}',
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


def get_dest_path(dest_dir: str, path: str, file_name: str, index: dict, descent: int = None):
    try:
        if index:
            try:
                _res = get_from_index(index, path, file_name)
            except KeyError:
                _res = None

            if _res:
                _path = os.path.dirname(_res)
                _file = os.path.basename(_res)
                _path = os.path.join(
                    '..',
                    '' if descent is None else '..',  # в режиме с descent корень находится на уровень выше
                    _path
                )

                try:
                    helper.makedirs(os.path.join(dest_dir, _path), exist_ok=True)
                except FileExistsError:
                    pass
                return _path, _file

        return path, file_name
    except Exception as err:
        raise ExtException(
            parent=err,
            message='Ошибка получения пути из index.json',
            detail=f'{path}\{file_name}',
            action='CodeOrganizer.get_dest_path',
        ) from err
