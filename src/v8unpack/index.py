import os
import json


def get(index: dict, path: str, file_name: str):
    _index = index
    if path:
        _path = path.split('\\')
        for _dir in _path:
            _index = _index[_dir]
    return _index[file_name]


def create_index(index_file_name, src_dir, dest_dir):
    def _create_index(_index, _src_dir, _dest_dir, _path):
        entries = os.listdir(os.path.join(_src_dir, _path))
        for entry in entries:
            new_path = os.path.join(_path, entry)
            if os.path.isdir(os.path.join(_src_dir, new_path)):
                if entry not in _index:
                    _index[entry] = {}
                _create_index(_index[entry], _src_dir, _dest_dir, new_path)
            else:
                if entry not in _index:
                    _index[entry] = os.path.join(_dest_dir, _path, entry) if _dest_dir else ''
        pass

    try:
        with open(index_file_name, 'r', encoding='utf-8') as f:
            index = json.load(f)
    except FileNotFoundError:
        index = {}

    _create_index(index, src_dir, dest_dir, '')
    with open(index_file_name, 'w+', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
