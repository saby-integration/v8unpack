import os
import shutil
from datetime import datetime

from . import helper
from .ext_exception import ExtException
from .organizer_code import OrganizerCode
from .organizer_form_elem import OrganizerFormElem


class OrganizerFile:

    @classmethod
    def unpack(cls, src_dir, dest_dir, *, pool=None, index=None, descent=None):
        begin = datetime.now()
        print(f'{"Организуем код":30}')
        tasks_code_file = []
        tasks_form_elem = []
        helper.clear_dir(dest_dir)
        cls._unpack(src_dir, os.path.abspath(dest_dir), '', tasks_code_file, tasks_form_elem, index,
                    descent)
        helper.run_in_pool(cls.unpack_code_file, tasks_code_file, pool=pool,
                           title=f'{"Раскладываем код по файлам":30}')
        helper.run_in_pool(OrganizerFormElem.unpack, tasks_form_elem, pool=pool,
                           title=f'{"Раскладываем элементы форм":30}')
        print(f'{"Организуем код - готово":30}: {datetime.now() - begin}')

    @classmethod
    def _unpack(cls, src_dir, dest_dir, path, tasks_code_file, tasks_form_elem, index, descent=None):
        entries = os.listdir(os.path.join(src_dir, path))
        for entry in entries:
            try:
                src_entry_path = os.path.join(src_dir, path, entry)

                if os.path.isdir(src_entry_path):
                    new_path = os.path.join(path, entry)
                    cls._unpack(src_dir, dest_dir, new_path, tasks_code_file, tasks_form_elem, index, descent)
                    continue
                if entry[-4:] == '.bsl':
                    tasks_code_file.append((src_dir, path, entry, dest_dir, index, descent))
                elif entry[-17:] in ['.elements803.json', '.elements802.json']:
                    tasks_form_elem.append((src_dir, path, entry, dest_dir, index, descent))
                else:
                    src_path = os.path.join(src_dir, path)
                    cls.unpack_file(src_path, entry, dest_dir, path, entry, index, descent)
            except Exception as err:
                raise ExtException(
                    parent=err,
                    action=f'{cls.__name__}._unpack {path}.{entry}'
                ) from err

    @classmethod
    def unpack_file(cls, src_path, src_file_name, dest_dir, dest_path, dest_file_name, index, descent=None):
        try:
            dest_entry_path, dest_file_name = OrganizerCode.get_dest_path(dest_dir, dest_path, dest_file_name, index,
                                                                          descent)
            dest_full_path = os.path.abspath(os.path.join(dest_dir, dest_entry_path))

            if dest_entry_path:
                helper.makedirs(dest_full_path, exist_ok=True)

            src_full_path = os.path.join(src_path, src_file_name)

            # файлы вне папки исходников не версионируются
            if dest_full_path.startswith(dest_dir) or os.path.normcase(dest_entry_path).find('\\src\\') >= 0:
                descent_full_dest_path, descent_file_name = cls.unpack_get_descent_filename(src_path, src_file_name,
                                                                                            None,
                                                                                            dest_full_path,
                                                                                            dest_file_name,
                                                                                            descent,
                                                                                            cls.equal_binary_file)
            else:
                descent_full_dest_path, descent_file_name = os.path.join(dest_dir, dest_entry_path), dest_file_name

            if descent_file_name:
                shutil.copy(src_full_path, os.path.join(descent_full_dest_path, descent_file_name))
        except Exception as err:
            raise ExtException(parent=err, action=f'{cls.__name__}.unpack_file {src_file_name}') from err

    @classmethod
    def unpack_code_file(cls, params):
        src_dir, path, file_name, dest_dir, index, descent = params
        try:
            code_areas = OrganizerCode.unpack(params)
            for elem in code_areas:
                _file = code_areas[elem]
                if elem == 'root':
                    _file['path'], _file['file_name'] = OrganizerCode.get_dest_path(dest_dir, path, file_name, index,
                                                                                    descent)
                else:
                    if _file['area_type'] == 'includr':
                        continue
                    _file['path'], _file['file_name'] = OrganizerCode.parse_include_path(
                        elem, path, file_name, index.get('Области include') if index else None, descent)
                _file['dest_path'] = os.path.abspath(os.path.join(dest_dir, _file['path']))
                if _file['dest_path'].startswith(dest_dir) or os.path.normcase(_file['path']).find('\\src\\') >= 0:
                    descent_full_dest_path, descent_file_name = cls.unpack_get_descent_filename(
                        None, None, _file['data'], _file['dest_path'], _file['file_name'], descent,
                        cls.equal_code_file)
                else:
                    descent_full_dest_path, descent_file_name = _file['dest_path'], _file['file_name']

                if descent_file_name:
                    helper.txt_write(_file['data'], descent_full_dest_path, descent_file_name)
        except Exception as err:
            raise ExtException(
                parent=err,
                dump={"filename": os.path.join(src_dir, path, file_name)},
                action='unpack_code_file'
            )

    @classmethod
    def equal_binary_file(cls, src_path, src_file_name, src_data, near_descent_path, near_descent_file_name):
        with open(os.path.join(near_descent_path, near_descent_file_name), 'rb') as near_file:
            with open(os.path.join(src_path, src_file_name), 'rb') as src_file:
                near_data = near_file.read()
                src_data = src_file.read()
                if near_data == src_data:  # если файл не менялся, ничего с ним не делаем
                    return True
        return False

    @classmethod
    def equal_code_file(cls, src_path, src_file_name, src_data, near_descent_path, near_descent_file_name):
        near_data = helper.txt_read(near_descent_path, near_descent_file_name)
        if near_data == src_data:  # если файл не менялся, ничего с ним не делаем
            return True
        return False

    @classmethod
    def unpack_get_descent_filename(cls, src_path, src_file_name, src_data, dest_path, dest_file_name, descent,
                                    comparer):
        return dest_path, dest_file_name

    @classmethod
    def pack(cls, src_dir, dest_dir, *, pool=None, index=None, descent=None):
        begin = datetime.now()
        print(f'{"Собираем код":30}')
        try:
            helper.clear_dir(dest_dir)
            tasks_code_file = []
            tasks_form_elem = []
            src_dir = os.path.abspath(src_dir)
            index_code_areas = index.get('Области include') if index else None
            if index:
                cls._pack_index(src_dir, dest_dir, tasks_code_file, tasks_form_elem, index, index_code_areas, [''], descent)
            cls._pack(src_dir, dest_dir, '', tasks_code_file, tasks_form_elem, index, index_code_areas, descent)
            helper.run_in_pool(OrganizerCode.pack, tasks_code_file, pool=pool, title=f'{"Собираем код из файлов":30}')
            helper.run_in_pool(OrganizerFormElem.pack, tasks_form_elem, pool=pool,
                               title=f'{"Собираем элементы форм":30}')
        except Exception as err:
            raise ExtException(parent=err)
        print(f'{"Собираем код - готово":30}: {datetime.now() - begin}')

    @classmethod
    def _pack_index(cls, src_dir: str, dest_dir: str, tasks_code_file: list, tasks_form_elem, index: dict, index_code_areas: dict, path: list,
                    descent=None):
        for entry in index:
            try:
                if entry == 'Области include':
                    continue
                if not index[entry]:
                    continue
                if isinstance(index[entry], dict):
                    path.append(entry)
                    cls._pack_index(src_dir, dest_dir, tasks_code_file, tasks_form_elem, index[entry], index_code_areas, path, descent)
                    path.pop()
                    pass
                elif isinstance(index[entry], str):
                    _src_path = os.path.join(
                        '..',
                        '' if descent is None else '..',  # в режиме с descent корень находится на уровень выше
                        os.path.dirname(index[entry])
                    )
                    _dest_path = os.path.join(*path)
                    if entry[-4:] == '.bsl':
                        _src_abs_path = os.path.abspath(_src_path)
                        if os.path.normcase(_src_path).find('\\src\\') >= 0:
                            func_descent_filename = cls.pack_get_descent_filename
                        else:
                            func_descent_filename = OrganizerFile.pack_get_descent_filename
                        tasks_code_file.append((
                            src_dir, _src_path, os.path.basename(index[entry]),
                            dest_dir, _dest_path, entry, index_code_areas,
                            descent, func_descent_filename))
                    elif entry[-17:] in ['.elements803.json', '.elements802.json']:
                        tasks_form_elem.append((
                            src_dir, _src_path, os.path.basename(index[entry]),
                            dest_dir, _dest_path, entry, index_code_areas, descent,
                            cls.pack_get_descent_filename))
                    else:
                        _dest_path = os.path.join(dest_dir, *path)
                        _src_path = os.path.join(
                            '..',
                            '' if descent is None else '..',  # в режиме с descent корень находится на уровень выше
                            index[entry]
                        )
                        _src_full_path = os.path.join(
                            src_dir,
                            _src_path
                        )
                        _src_path = os.path.dirname(_src_full_path)
                        _src_file_name = os.path.basename(_src_full_path)
                        if os.path.normcase(_src_path).find('\\src\\') >= 0:
                            _src_path, _src_file_name = cls.pack_get_descent_filename(_src_path, _src_file_name,
                                                                                      descent)
                        cls._pack_file(_src_path, _src_file_name, _dest_path, entry, descent)
                else:
                    raise Exception('Некорректный формат файла индекса')
            except FileNotFoundError:
                pass
            except Exception as err:
                raise ExtException(parent=err)

    @classmethod
    def pack_get_descent_filename(cls, src_path, src_file_name, descent):
        return src_path, src_file_name

    @classmethod
    def list_descent_dir(cls, src_dir, path, descent):
        return os.listdir(os.path.join(src_dir, path))

    @classmethod
    def _pack(cls, src_dir, dest_dir, path, tasks_code_file, tasks_form_elem, index, index_code_areas, descent=None):
        if path:
            helper.makedirs(os.path.join(dest_dir, path), exist_ok=True)
        entries = cls.list_descent_dir(src_dir, path, descent)
        for entry in entries:
            try:
                src_entry_path = os.path.join(src_dir, path, entry)

                if os.path.isdir(src_entry_path):
                    cls._pack(src_dir, dest_dir, os.path.join(path, entry), tasks_code_file, tasks_form_elem, index,
                              index_code_areas, descent)
                    continue
                _src_path = os.path.join(src_dir, path)
                descent_full_src_path, descent_file_name = cls.pack_get_descent_filename(
                    _src_path, entry, descent)
                if os.path.isfile(os.path.join(dest_dir, path, entry)):
                    # если файл уже есть, значит он был переопределен в индексе и делать ничего не надо
                    continue
                if entry[-4:] == '.bsl':
                    tasks_code_file.append((
                        src_dir, path, descent_file_name, dest_dir, path, entry, index_code_areas, descent,
                        cls.pack_get_descent_filename))
                elif entry[-17:] in ['.elements803.json', '.elements802.json']:
                    tasks_form_elem.append((
                        src_dir, path, descent_file_name, dest_dir, path, entry, index_code_areas, descent,
                        cls.pack_get_descent_filename))
                else:
                    # shutil.copy(src_entry_path, os.path.join(dest_dir, path, entry))
                    _dest_path = os.path.join(dest_dir, path)
                    cls._pack_file(descent_full_src_path, descent_file_name, _dest_path, entry, descent)
            except Exception as err:
                raise ExtException(parent=err, action=f'{cls.__name__}._pack', detail=f'{entry} {path}')

    @classmethod
    def _pack_file(cls, src_path, src_file_name, dest_path, dest_file_name, descent=None):
        _src_path = os.path.join(src_path, src_file_name)
        _dest_path = os.path.join(dest_path, dest_file_name)
        try:
            shutil.copy(_src_path, _dest_path)
        except FileNotFoundError:
            _dest_dir = os.path.dirname(_dest_path)
            helper.makedirs(_dest_dir, exist_ok=True)
            shutil.copy(_src_path, _dest_path)
