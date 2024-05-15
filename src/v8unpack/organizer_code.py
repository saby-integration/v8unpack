import os

from . import helper
from .ext_exception import ExtException
from .index import get as get_from_index


class OrganizerCode:
    def __init__(self):
        self.code_areas = None
        self.data = None

    @staticmethod
    def is_area(name):
        area_type = name[:17]
        is_area = area_type in ('#Область include_', '#Область includr_')
        if is_area:
            return area_type[9:-1]
        return None

    @classmethod
    def unpack(cls, params):
        src_dir, path, file_name, dest_dir, index, descent = params
        self = cls()
        self.code_areas = {'root': dict(data='')}
        _path = ['']
        _include_path = ['root']
        with open(os.path.join(src_dir, path, file_name), 'r', encoding='utf-8-sig') as file:
            line = file.readline()
            while line:
                try:
                    _line = line.strip()
                    if line.endswith('//DynamicDirective'):
                        directive_begin = line.find('&')
                        if directive_begin >= 0:
                            line = f'{line[0:directive_begin]}//DynamicDirective'
                    if _line and _line[0] == '#':
                        if _line.startswith('#Область'):
                            area_type = cls.is_area(_line)
                            if area_type:
                                key = _line[17:].strip()
                                # if key in self.code_areas:
                                #     raise Exception(
                                #         f'В {path}{file_name} ссылка на один и тот же файл у разных областей {key}')
                                self.code_areas[_include_path[-1]]['data'] += line
                                self.code_areas[key] = dict(data='', area_type=area_type)
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
    def pack(cls, params):
        src_dir, src_path, src_file_name, dest_dir, dest_path, dest_file_name, index_code_areas, \
        descent, pack_get_descent_filename = params
        data = cls.pack_file(src_dir, src_path, src_file_name, index_code_areas, descent, pack_get_descent_filename)
        helper.txt_write(data, os.path.join(dest_dir, dest_path), dest_file_name)

    @classmethod
    def pack_file(cls, src_dir, path, file_name, index_code_areas, descent, pack_get_descent_filename,
                  dynamic_directive=None):
        try:
            data = ''
            _src_abs_path = os.path.abspath(os.path.join(src_dir, path))
            if _src_abs_path.startswith(src_dir) or os.path.normcase(path).find('\\src\\') >= 0:
                _src_abs_path, file_name = pack_get_descent_filename(_src_abs_path, file_name, descent)

            with open(os.path.join(_src_abs_path, file_name), 'r', encoding='utf-8') as file:
                line = file.readline()
                while line:
                    _line = line.strip()
                    if _line:
                        if _line.startswith('//DynamicDirective') and dynamic_directive:
                            line = f'{dynamic_directive}{line}'
                    data += line
                    if _line and _line[0] == '#':
                        if cls.is_area(_line):
                            area_name_parts = _line[17:].strip().split('//')
                            include_path = area_name_parts[0]

                            dynamic_directive = area_name_parts[1] if len(area_name_parts) > 1 else dynamic_directive

                            _path, _file_name = cls.parse_include_path(include_path, path, file_name, index_code_areas,
                                                                       descent)
                            _src_abs_path = os.path.abspath(os.path.join(src_dir, _path))
                            if _src_abs_path.startswith(src_dir) or os.path.normcase(_path).find('\\src\\') >= 0:
                                _path, _file_name = pack_get_descent_filename(_src_abs_path, _file_name, descent)
                            data += cls.pack_file(src_dir, _path, _file_name, index_code_areas, descent,
                                                  pack_get_descent_filename, dynamic_directive)
                    line = file.readline()
                return data
        except ExtException as err:
            raise ExtException(
                parent=err,
                action=f'{cls.__name__}.pack_file {file_name}') from err
        except Exception as err:
            raise ExtException(
                parent=err,
                action=f'{cls.__name__}.pack_file {file_name}',
                message='Ошибка упаковки файла', detail=f'{os.path.join(path, file_name)}: {err}') from err

    @staticmethod
    def parse_include_path(include_path, path, file_name, index_code_areas, descent=None, *, file_extension='bsl'):
        if index_code_areas and include_path in index_code_areas:
            include_path = index_code_areas[include_path]
        tmp = include_path.split('_')
        size_tmp = len(tmp)
        if size_tmp == 0:
            raise Exception(f'{path} {file_name} в include не указан путь')
        _file_name = f'{tmp[-1]}.{file_extension}'
        _path = '..'  # include не должен лежать внутри папки с исходниками
        if descent is not None:
            _path = os.path.join(_path, '..')
        if size_tmp > 1:
            tmp = ['..' if elem == '' else elem for elem in tmp[:-1]]
            _path = os.path.join(_path, *tmp)
        if _path == '..':
            _path = path
        return _path, _file_name

    @staticmethod
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
