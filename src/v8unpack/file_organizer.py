import os
import shutil

from . import helper
from .code_organizer import CodeOrganizer
from .ext_exception import ExtException


class FileOrganizer:

    @classmethod
    def unpack(cls, src_dir, dest_dir, *, pool=None, index=None, descent=None):
        tasks = []
        cls._unpack(src_dir, os.path.abspath(dest_dir), '', tasks, index, descent)
        helper.run_in_pool(cls.unpack_code_file, tasks, pool=pool)

    @classmethod
    def _unpack(cls, src_dir, dest_dir, path, tasks, index, descent=None):
        entries = os.listdir(os.path.join(src_dir, path))
        for entry in entries:
            src_entry_path = os.path.join(src_dir, path, entry)

            if os.path.isdir(src_entry_path):
                new_path = os.path.join(path, entry)
                cls._unpack(src_dir, dest_dir, new_path, tasks, index, descent)
                continue
            if entry[-3:] == '.1c':
                tasks.append((src_dir, path, entry, dest_dir, index, descent))
            else:
                src_path = os.path.join(src_dir, path)
                cls.unpack_file(src_path, entry, dest_dir, path, entry, index, descent)

    @classmethod
    def unpack_file(cls, src_path, src_file_name, dest_dir, dest_path, dest_file_name, index, descent=None):
        dest_entry_path, dest_file_name = CodeOrganizer.get_dest_path(dest_dir, dest_path, dest_file_name, index)
        dest_full_path = os.path.abspath(os.path.join(dest_dir, dest_entry_path))

        if dest_entry_path:
            os.makedirs(dest_full_path, exist_ok=True)

        src_full_path = os.path.join(src_path, src_file_name)

        if dest_full_path.startswith(dest_dir):  # файлы вне папки исходников не версионируются
            descent_full_dest_path, descent_file_name = cls.unpack_get_descent_filename(src_path, src_file_name, None,
                                                                                        dest_full_path, dest_file_name,
                                                                                        descent,
                                                                                        cls.equal_binary_file)
        else:
            descent_full_dest_path, descent_file_name = os.path.join(dest_dir, dest_entry_path), dest_file_name

        if descent_file_name:
            shutil.copy(src_full_path, os.path.join(descent_full_dest_path, descent_file_name))

    @classmethod
    def unpack_code_file(cls, src_dir, path, file_name, dest_dir, index, descent=None):
        try:
            code_areas = CodeOrganizer.unpack(src_dir, path, file_name, dest_dir, index)
            for elem in code_areas:
                _file = code_areas[elem]
                if elem == 'root':
                    _file['path'], _file['file_name'] = CodeOrganizer.get_dest_path(dest_dir, path, file_name, index)
                else:
                    _file['path'], _file['file_name'] = CodeOrganizer.parse_include_path(elem, path, file_name)
                _file['dest_path'] = os.path.abspath(os.path.join(dest_dir, _file['path']))
                if _file['dest_path'].startswith(dest_dir):
                    descent_full_dest_path, descent_file_name = cls.unpack_get_descent_filename(
                        None, None, _file['data'], _file['dest_path'], _file['file_name'], descent, cls.equal_code_file)
                else:
                    descent_full_dest_path, descent_file_name = _file['dest_path'], _file['file_name']

                if descent_file_name:
                    os.makedirs(descent_full_dest_path, exist_ok=True)
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
        helper.clear_dir(dest_dir)
        tasks = []
        src_dir = os.path.abspath(src_dir)
        cls.pack_index(src_dir, dest_dir, tasks, index, descent)
        cls._pack(src_dir, dest_dir, '', tasks, index, descent)
        helper.run_in_pool(CodeOrganizer.pack, tasks, pool=pool)

    @classmethod
    def pack_index(cls, src_dir: str, dest_dir: str, tasks: list, index: dict, descent=None):
        if index:
            cls._pack_index(src_dir, dest_dir, tasks, index, [''], descent)

    @classmethod
    def _pack_index(cls, src_dir: str, dest_dir: str, tasks: list, index: dict, path: list, descent=None):
        for entry in index:
            if not index[entry]:
                continue
            if isinstance(index[entry], dict):
                path.append(entry)
                cls._pack_index(src_dir, dest_dir, tasks, index[entry], path, descent)
                path.pop()
                pass
            elif isinstance(index[entry], str):
                if entry[-3:] == '.1c':
                    _src_path = os.path.join('..', os.path.dirname(index[entry]))
                    _dest_path = os.path.join(*path)

                    _src_abs_path = os.path.abspath(_src_path)
                    if _src_abs_path.startswith(src_dir):
                        func_descent_filename = cls.pack_get_descent_filename
                    else:
                        func_descent_filename = FileOrganizer.pack_get_descent_filename
                    tasks.append((
                        src_dir, _src_path, os.path.basename(index[entry]),
                        dest_dir, _dest_path, entry,
                        descent, func_descent_filename))
                else:
                    _dest_path = os.path.join(dest_dir, *path)
                    _src_full_path = os.path.join(src_dir, '..', index[entry])
                    _src_path = os.path.dirname(_src_full_path)
                    _src_file_name = os.path.basename(_src_full_path)
                    cls._pack_file(_src_path, _src_file_name, _dest_path, entry, descent)
            else:
                raise Exception('Некорректный формат файла индекса')

    @classmethod
    def pack_get_descent_filename(cls, src_path, src_file_name, descent):
        return src_path, src_file_name

    @classmethod
    def list_descent_dir(cls, src_dir, path, descent):
        return os.listdir(os.path.join(src_dir, path))

    @classmethod
    def _pack(cls, src_dir, dest_dir, path, tasks, index, descent=None):
        if path:
            os.makedirs(os.path.join(dest_dir, path), exist_ok=True)
        entries = cls.list_descent_dir(src_dir, path, descent)
        for entry in entries:
            try:
                src_entry_path = os.path.join(src_dir, path, entry)

                if os.path.isdir(src_entry_path):
                    cls._pack(src_dir, dest_dir, os.path.join(path, entry), tasks, index, descent)
                    continue
                _src_path = os.path.join(src_dir, path)
                descent_full_src_path, descent_file_name = cls.pack_get_descent_filename(
                    _src_path, entry, descent)

                if entry[-3:] == '.1c':
                    tasks.append((
                        src_dir, path, descent_file_name, dest_dir, path, entry, descent,
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
            os.makedirs(_dest_dir, exist_ok=True)
            shutil.copy(_src_path, _dest_path)
