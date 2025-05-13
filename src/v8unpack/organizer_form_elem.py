import os

from . import helper
from .ext_exception import ExtException, KeyNotFound
from .index import get_dest_path
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
        areas['root'] = elements
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
        try:
            for elem in tree:
                name: str = elem['name']
                area_type = cls.is_area(name)
                old_path = f'{path}/{name}' if path else name
                if area_type:
                    _path = path[len(path):]
                    new_path = f'{_path}/{name}' if _path else name
                    area_name = name[8:]
                    area = dict(
                        data={
                            # new_path: root_data.pop(old_path)
                        },
                        tree=elem.pop('child', [])
                    )
                    # в пути детей includr не используется.
                    name: str = f'include_{area_name}'
                    old_path = f'{path}/{name}' if path else name
                    cls._pop_area_data(area['tree'], old_path, root_data, area['data'], path)
                    elem['child'] = 'В отдельном файле'
                    if area_type == 'include_':  # includr_ только чтение
                        areas[area_name] = area
                    continue
                child = elem.get('child')
                if child:
                    cls._unpack_get_areas(child, old_path, root_data, areas)

        except Exception as err:
            raise ExtException(parent=err)

    @classmethod
    def _pop_area_data(cls, tree, path, root_data, data, remove_path):
        try:
            size_prefix = len(remove_path)
            if tree:
                for elem in tree:
                    name: str = elem['name']
                    old_path = f'{path}/{name}'
                    new_path = f'{path[size_prefix + 1:] if size_prefix else path}/{name}'
                    try:
                        data[new_path] = root_data.pop(old_path)
                    except Exception:
                        raise KeyNotFound(message='Не найден элемент формы', detail=old_path)
                    child = elem.get('child')
                    if child:
                        cls._pop_area_data(child, old_path, root_data, data, remove_path)

            pages = root_data.pop(f'{path}/-pages-', None)
            if pages is not None:
                new_path = f'{path[size_prefix + 1:] if size_prefix else path}/-pages-'
                data[new_path] = pages
                for name in pages:
                    old_path = f'{path}/{name}'
                    new_path = f'{path[size_prefix + 1:] if size_prefix else path}/{name}'
                    try:
                        data[new_path] = root_data.pop(old_path)
                    except KeyError:
                        pass
                        # raise KeyNotFound(message='Не найден элемент формы', detail=old_path)

        except Exception as err:
            raise ExtException(parent=err)

    @staticmethod
    def _unpack_write_areas(src_dir, path, file_name, dest_dir, index, descent, areas):
        try:
            for elem in areas:
                if elem == 'root':
                    dest_entry_path, dest_file_name = get_dest_path(dest_dir, path, file_name, index, descent)
                else:
                    dest_entry_path, dest_file_name = OrganizerCode.parse_include_path(
                        elem, path, elem, index.get('Области include') if index else None, descent,
                        file_extension=file_name[-9::])
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
        try:
            cls._pack_get_areas(src_dir, src_path, src_file_name, elements['tree'], '', elements['data'],
                                index_code_areas, descent)
        except Exception as err:
            raise ExtException(parent=err, message='Ошибка сборки элементов формы',
                               detail=f'{os.path.join(src_path, src_file_name)}')

        helper.json_write(elements, os.path.join(dest_dir, dest_path), dest_file_name)

    @staticmethod
    def form_elem_class(version, elem_type):
        elem_class = helper.get_class(f'v8unpack.MetaDataObject.Form.Form{version}Elements.FormElement.FormElement')
        return elem_class.get_class_form_elem(elem_type)

    @classmethod
    def _pack_get_areas(cls, src_dir, src_path, file_name, tree, path, root_data, index_code_areas, descent):
        for elem in tree:
            try:
                name: str = elem['name']
                new_path = f'{path}/{name}' if path else name
                area_type = cls.is_area(name)
                if area_type:
                    area_name = name[8:]
                    _path, _file_name = OrganizerCode.parse_include_path(
                        area_name, src_path, file_name, index_code_areas, descent, file_extension=file_name[-9::])
                    _src_abs_path = os.path.abspath(os.path.join(src_dir, _path))

                    include_elements = helper.json_read(_src_abs_path, _file_name)
                    cls._append_area_data(include_elements['tree'], name, root_data, include_elements['data'],
                                          path, area_type)
                    elem['child'] = include_elements['tree']
                    continue
                child = elem.get('child')
                if child:
                    cls._pack_get_areas(src_dir, src_path, file_name, child, new_path, root_data, index_code_areas,
                                        descent)
            except Exception as err:
                raise ExtException(parent=err, message='Ошибка сборки области формы', detail=elem['name'])

    @classmethod
    def _append_area_data(cls, tree, path, root_data, data, append_path, area_type=None):
        try:
            _path = f'include_{path[8:]}' if area_type == 'includr_' else path
            if tree:
                for elem in tree:
                    name: str = elem['name']
                    old_path = f'{_path}/{name}'
                    new_path = f'{append_path}/{_path}/{name}' if append_path else f'{_path}/{name}'
                    try:
                        root_data[new_path] = data.pop(old_path)
                    except Exception:
                        raise KeyNotFound(message='Не найден элемент формы', detail=old_path)
                    child = elem.get('child')
                    if child:
                        cls._append_area_data(child, old_path, root_data, data, append_path)

            pages = data.pop(f'{path}/-pages-', None)
            if pages is not None:
                new_path = f'{append_path}/{_path}/-pages-' if append_path else f'{_path}/-pages-'
                root_data[new_path] = pages
                for name in pages:
                    old_path = f'{path}/{name}'
                    new_path = f'{append_path}/{_path}/{name}' if append_path else f'{_path}/{name}'
                    try:
                        root_data[new_path] = data.pop(old_path)
                    except KeyError:
                        pass
                        # raise KeyNotFound(message='Не найден элемент формы', detail=old_path)
        except Exception as err:
            raise ExtException(parent=err)

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
