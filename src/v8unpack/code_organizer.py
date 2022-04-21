import os

from . import helper
from .ext_exception import ExtException
from .index import get as get_from_index


class CodeOrganizer:
    def __init__(self):
        self.code_areas = None
        self.data = None

    @classmethod
    def unpack_mp(cls, params):
        return cls.unpack(*params)

    @classmethod
    def unpack(cls, src_dir, path, file_name, dest_dir, index):
        self = cls()
        self.code_areas = {'root': dict(data='')}
        _path = ['']
        _include_path = ['root']
        with open(os.path.join(src_dir, path, file_name), 'r', encoding='utf-8-sig') as file:
            line = file.readline()
            while line:
                try:
                    _line = line.strip()
                    if _line and _line[0] == '#':
                        if _line.startswith('#Область'):
                            if _line.startswith('#Область include'):
                                key = _line[17:].strip()
                                # if key in self.code_areas:
                                #     raise Exception(
                                #         f'В {path}{file_name} ссылка на один и тот же файл у разных областей {key}')
                                self.code_areas[_include_path[-1]]['data'] += line
                                self.code_areas[key] = dict(data='')
                                _include_path.append(key)
                                _path.append(key)
                            else:
                                self.code_areas[_include_path[-1]]['data'] += line
                                _path.append('')

                        elif _line.startswith('#КонецОбласти'):
                            if _path[-1]:  # кончилась include область
                                _include_path.pop()
                            _path.pop()
                            self.code_areas[_include_path[-1]]['data'] += line
                        else:
                            self.code_areas[_include_path[-1]]['data'] += line
                    else:
                        self.code_areas[_include_path[-1]]['data'] += line
                    line = file.readline()
                except Exception as err:
                    raise ExtException(parent=err, detail=f'in file {file_name} line {line}') from err
        return self.code_areas

    @classmethod
    def pack_mp(cls, params):
        return cls.pack(*params)

    @classmethod
    def pack(cls, src_dir, src_path, src_file_name, dest_dir, dest_path, dest_file_name, index_code_areas, descent,
             pack_get_descent_filename):
        data = cls.pack_file(src_dir, src_path, src_file_name, index_code_areas, descent, pack_get_descent_filename)
        helper.txt_write(data, os.path.join(dest_dir, dest_path), dest_file_name)

    @classmethod
    def pack_file(cls, src_dir, path, file_name, index_code_areas, descent, pack_get_descent_filename):
        try:
            data = ''
            with open(os.path.join(src_dir, path, file_name), 'r', encoding='utf-8') as file:
                line = file.readline()
                while line:
                    data += line
                    _line = line.strip()
                    if _line and _line[0] == '#':
                        if _line.startswith('#Область include'):
                            include_path = _line[17:].strip()
                            _path, _file_name = cls.parse_include_path(include_path, path, file_name, index_code_areas,
                                                                       descent)
                            _src_abs_path = os.path.abspath(os.path.join(src_dir, _path))
                            if _src_abs_path.startswith(src_dir):
                                _path, _file_name = pack_get_descent_filename(_src_abs_path, _file_name, descent)
                            data += cls.pack_file(src_dir, _path, _file_name, index_code_areas, descent,
                                                  pack_get_descent_filename)
                    line = file.readline()
                return data
        except Exception as err:
            raise ExtException(parent=err, action=f'{cls.__name__}.pack_file', detail=f'{path} {file_name}')

    @staticmethod
    def parse_include_path(include_path, path, file_name, index_code_areas, descent):
        if index_code_areas and include_path in index_code_areas:
            include_path = index_code_areas[include_path]
        tmp = include_path.split('_')
        size_tmp = len(tmp)
        if size_tmp == 0:
            raise Exception(f'{path} {file_name} в include не указан путь')
        _file_name = f'{tmp[-1]}.1c'
        _path = '..'  # include не должен лежать внутри папки с исходниками
        if descent:
            _path = os.path.join(_path, '..')
        if size_tmp > 1:
            tmp = ['..' if elem == '' else elem for elem in tmp[:-1]]
            _path = os.path.join(_path, *tmp)
        return _path, _file_name

    @staticmethod
    def get_dest_path(dest_dir: str, path: str, file_name: str, index: dict, descent: int):
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
                    os.makedirs(os.path.join(dest_dir, _path), exist_ok=True)
                except FileExistsError:
                    pass
                return _path, _file

        return path, file_name
