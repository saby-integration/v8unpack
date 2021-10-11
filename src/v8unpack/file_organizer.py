import os
from .code_organizer import CodeOrganizer
import shutil
from . import helper


class FileOrganizer:

    @classmethod
    def unpack(cls, src_dir, dest_dir, *, pool=None, index=None):
        tasks = []
        cls._unpack(src_dir, dest_dir, '', tasks, index)
        helper.run_in_pool(CodeOrganizer.unpack, tasks, pool=pool)

    @classmethod
    def _unpack(cls, src_dir, dest_dir, path, tasks, index):
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
                dest_entry_path = CodeOrganizer.get_dest_path(dest_dir, path, entry, index)
                if dest_entry_path:
                    os.makedirs(os.path.join(dest_dir, dest_entry_path), exist_ok=True)
                new_dest = os.path.join(dest_dir, dest_entry_path, entry)
                shutil.copy(src_entry_path, new_dest)

    @classmethod
    def pack(cls, src_dir, dest_dir, *, pool=None, index=None):
        helper.clear_dir(dest_dir)
        tasks = []
        cls.pack_index(src_dir, dest_dir, tasks, index)
        cls._pack(src_dir, dest_dir, '', tasks, index)
        helper.run_in_pool(CodeOrganizer.pack, tasks, pool=pool)

    @classmethod
    def pack_index(cls, src_dir: str, dest_dir: str, tasks: list, index: dict):
        if index:
            cls._pack_index(src_dir, dest_dir, tasks, index, [''])

    @classmethod
    def _pack_index(cls, src_dir: str, dest_dir: str, tasks: list, index: dict, path: list):
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
                    tasks.append((src_dir, _src_path, entry, dest_dir, _dest_path))
                else:
                    _dest_full_path = os.path.join(dest_dir, *path, entry)
                    _src_path = os.path.join(src_dir, '..', index[entry])
                    try:
                        shutil.copy(_src_path, _dest_full_path)
                    except FileNotFoundError:
                        _dest_dir = os.path.dirname(_dest_full_path)
                        os.makedirs(_dest_dir, exist_ok=True)
                        shutil.copy(_src_path, _dest_full_path)
            else:
                raise Exception('Некорректный формат файла индекса')

    @classmethod
    def _pack(cls, src_dir, dest_dir, path, tasks, index):
        if path:
            os.makedirs(os.path.join(dest_dir, path), exist_ok=True)
        entries = os.listdir(os.path.join(src_dir, path))
        for entry in entries:
            src_entry_path = os.path.join(src_dir, path, entry)

            if os.path.isdir(src_entry_path):
                cls._pack(src_dir, dest_dir, os.path.join(path, entry), tasks, index)
                continue
            if entry[-3:] == '.1c':
                tasks.append((src_dir, path, entry, dest_dir, path))
            else:
                shutil.copy(src_entry_path, os.path.join(dest_dir, path, entry))
