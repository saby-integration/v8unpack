import os
import shutil

from . import helper
from .code_organizer import CodeOrganizer


class FileOrganizer:

    @classmethod
    def unpack(cls, src_dir, dest_dir, *, pool=None, index=None, descent=None):
        tasks = []
        cls._unpack(src_dir, dest_dir, '', tasks, index)
        helper.run_in_pool(CodeOrganizer.unpack, tasks, pool=pool)

    @classmethod
    def _unpack(cls, src_dir, dest_dir, path, tasks, index, descent=None):
        entries = os.listdir(os.path.join(src_dir, path))
        for entry in entries:
            src_entry_path = os.path.join(src_dir, path, entry)

            if os.path.isdir(src_entry_path):
                new_path = os.path.join(path, entry)
                cls._unpack(src_dir, dest_dir, new_path, tasks, index)
                continue
            if entry[-3:] == '.1c':
                tasks.append((src_dir, path, entry, dest_dir, index))
            else:
                dest_entry_path, dest_file_name = CodeOrganizer.get_dest_path(dest_dir, path, entry, index)
                if dest_entry_path:
                    os.makedirs(os.path.join(dest_dir, dest_entry_path), exist_ok=True)
                dest_path = os.path.join(dest_dir, dest_entry_path)
                src_path = os.path.join(src_dir, path)
                cls._unpack_file(src_path, entry, dest_path, dest_file_name, descent)

    @classmethod
    def _unpack_file(cls, src_path, src_file_name, dest_path, dest_file_name, descent=None):
        _src_path = os.path.join(src_path, src_file_name)
        _dest_path = os.path.join(dest_path, dest_file_name)
        shutil.copy(_src_path, _dest_path)

    @classmethod
    def pack(cls, src_dir, dest_dir, *, pool=None, index=None, descent=None):
        helper.clear_dir(dest_dir)
        tasks = []
        cls.pack_index(src_dir, dest_dir, tasks, index)
        cls._pack(src_dir, dest_dir, '', tasks, index)
        helper.run_in_pool(CodeOrganizer.pack, tasks, pool=pool)

    @classmethod
    def pack_index(cls, src_dir: str, dest_dir: str, tasks: list, index: dict, descent=None):
        if index:
            cls._pack_index(src_dir, dest_dir, tasks, index, [''], descent=None)

    @classmethod
    def _pack_index(cls, src_dir: str, dest_dir: str, tasks: list, index: dict, path: list, descent=None):
        for entry in index:
            if not index[entry]:
                continue
            if isinstance(index[entry], dict):
                path.append(entry)
                cls._pack_index(src_dir, dest_dir, tasks, index[entry], path)
                path.pop()
                pass
            elif isinstance(index[entry], str):
                if entry[-3:] == '.1c':
                    _src_path = os.path.join('..', os.path.dirname(index[entry]))
                    _dest_path = os.path.join(*path)
                    tasks.append((src_dir, _src_path, os.path.basename(index[entry]), dest_dir, _dest_path, entry))
                else:
                    _dest_path = os.path.join(dest_dir, *path)
                    _src_full_path = os.path.join(src_dir, '..', index[entry])
                    _src_path = os.path.dirname(_src_full_path)
                    _src_file_name = os.path.basename(_src_full_path)
                    cls._pack_file(_src_path, _src_file_name, _dest_path, entry, descent)
            else:
                raise Exception('Некорректный формат файла индекса')

    @classmethod
    def _pack(cls, src_dir, dest_dir, path, tasks, index, descent=None):
        if path:
            os.makedirs(os.path.join(dest_dir, path), exist_ok=True)
        entries = os.listdir(os.path.join(src_dir, path))
        for entry in entries:
            src_entry_path = os.path.join(src_dir, path, entry)

            if os.path.isdir(src_entry_path):
                cls._pack(src_dir, dest_dir, os.path.join(path, entry), tasks, index)
                continue
            if entry[-3:] == '.1c':
                tasks.append((src_dir, path, entry, dest_dir, path, entry))
            else:
                shutil.copy(src_entry_path, os.path.join(dest_dir, path, entry))
                _dest_path = os.path.join(dest_dir, path)
                _src_path = os.path.join(src_dir, path)
                cls._pack_file(_src_path, entry, _dest_path, entry, descent)

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
