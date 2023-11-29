import os

from . import helper
from .ext_exception import ExtException, KeyNotFound
from .index import get as get_from_index
from .organizer_code import OrganizerCode


class OrganizerFormElem:
    def __init__(self):
        self.code_areas = None
        self.data = None

    @classmethod
    def unpack(cls, params):
        src_dir, path, file_name, dest_dir, index, descent = params
        areas = {}
        elements = helper.json_read(os.path.join(src_dir, path), file_name)
        cls._unpack_get_areas(elements['tree'], '', elements['data'], areas)
        areas['root'] = dict(tree=elements['tree'], data=elements['data'])
        cls._unpack_write_areas(src_dir, path, file_name, dest_dir, index, descent, areas)

    @staticmethod
    def is_area(name):
        area_type = name[:8]
        is_area = area_type in ('include_', 'includr_')
        if is_area:
            return area_type
        return None

    @classmethod
    def _unpack_get_areas(cls, tree, path, root_data, areas):
        for elem in tree:
            name: str = elem['name']
            new_path = f'{path}/{name}'
            area_type = cls.is_area(name)
            if area_type:
                area_name = name[8:]
                area = dict(
                    data={
                        new_path: root_data.pop(new_path)
                    },
                    tree=elem.pop('child', [])
                )
                cls._pop_area_data(area['tree'], new_path, root_data, area['data'])
                elem['child'] = 'В отдельном файле'
                if area_type == 'include_':  # includr_ только чтение
                    areas[area_name] = area
                continue
            child = elem.get('child')
            if child:
                cls._unpack_get_areas(child, new_path, root_data, areas)

    @classmethod
    def _pop_area_data(cls, tree, path, root_data, data):
        for elem in tree:
            name: str = elem['name']
            new_path = f'{path}/{name}'
            try:
                data[new_path] = root_data.pop(new_path)
            except Exception:
                raise KeyNotFound(message='Не найден элемент формы', detail=new_path)
            child = elem.get('child')
            if child:
                cls._pop_area_data(child, new_path, root_data, data)

    @staticmethod
    def _unpack_write_areas(src_dir, path, file_name, dest_dir, index, descent, areas):
        try:
            for elem in areas:
                if elem == 'root':
                    dest_entry_path, dest_file_name = OrganizerCode.get_dest_path(dest_dir, path, file_name, index,
                                                                                  descent)
                else:
                    dest_entry_path, dest_file_name = OrganizerCode.parse_include_path(
                        elem, path, elem, index.get('Области include') if index else None, descent,
                        file_extension=file_name[-16::])
                dest_path = os.path.abspath(os.path.join(dest_dir, dest_entry_path))

                helper.json_write(areas[elem], dest_path, dest_file_name)
        except Exception as err:
            raise ExtException(
                parent=err,
                dump={"filename": os.path.join(src_dir, path, file_name)},
                action='unpack_code_file'
            )

    @classmethod
    def pack(cls, params):
        src_dir, src_path, src_file_name, dest_dir, dest_path, dest_file_name, index_code_areas, \
        descent, pack_get_descent_filename = params
        elements = helper.json_read(os.path.join(src_dir, src_path), src_file_name)
        cls._pack_get_areas(src_dir, src_path, src_file_name, elements['tree'], '', elements['data'], index_code_areas)

        helper.json_write(elements, os.path.join(dest_dir, dest_path), dest_file_name)

    @classmethod
    def _pack_get_areas(cls, src_dir, src_path, file_name, tree, path, root_data, index_code_areas):
        for elem in tree:
            name: str = elem['name']
            new_path = f'{path}/{name}'
            area_type = cls.is_area(name)
            if area_type:
                area_name = name[8:]
                _path, _file_name = OrganizerCode.parse_include_path(area_name, src_path, file_name, index_code_areas,
                                                                     file_extension=file_name[-16::])
                _src_abs_path = os.path.abspath(os.path.join(src_dir, _path))
                include_elements = helper.json_read(_src_abs_path, _file_name)
                root_data.update(include_elements['data'])
                elem['child'] = include_elements['tree']
                continue
            child = elem.get('child')
            if child:
                cls._pack_get_areas(src_dir, src_path, file_name, child, new_path, root_data, index_code_areas)

    @staticmethod
    def parse_include_path(include_path, path, file_name, index_code_areas, descent):
        if index_code_areas and include_path in index_code_areas:
            include_path = index_code_areas[include_path]
        tmp = include_path.split('_')
        size_tmp = len(tmp)
        if size_tmp == 0:
            raise Exception(f'{path} {file_name} в include не указан путь')
        _file_name = f'{tmp[-1]}.bsl'
        _path = '..'  # include не должен лежать внутри папки с исходниками
        if descent is not None:
            _path = os.path.join(_path, '..')
        if size_tmp > 1:
            tmp = ['..' if elem == '' else elem for elem in tmp[:-1]]
            _path = os.path.join(_path, *tmp)
        return _path, _file_name

    @staticmethod
    def get_dest_path(dest_dir: str, path: str, file_name: str, index: dict, descent: int):
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
                detail=f'{path}/{file_name}',
                action='CodeOrganizer.get_dest_path',
            ) from err
