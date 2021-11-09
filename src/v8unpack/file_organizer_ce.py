import os

from . import helper
from .file_organizer import FileOrganizer


class FileOrganizerCE(FileOrganizer):

    @classmethod
    def unpack_get_descent_filename(cls, src_path, src_file_name, src_data, dest_path, dest_file_name, descent,
                                    comparer):
        # если есть файл нашей версии или новый файл отличается от старого, или старого файла нет
        # сохраняем файл с номером текущей версии
        # считаем, что общие изменения должны делаться на минимальной версии
        descent_file_name = helper.get_descent_file_name(dest_file_name, descent)
        descent_full_dest_path = os.path.join(dest_path, descent_file_name)

        if not os.path.isfile(descent_full_dest_path):  # если нет файла нужной версии
            near_descent_path, near_descent_file_name = helper.get_near_descent_file_name(dest_path, dest_file_name,
                                                                                          descent)
            if near_descent_file_name:  # нашли файл младшей версии
                if comparer(src_path, src_file_name, src_data, near_descent_path, near_descent_file_name):
                    return '', ''
        return dest_path, descent_file_name

    @classmethod
    def pack_get_descent_filename(cls, src_path, src_file_name, descent):
        descent_path, descent_file_name = helper.get_near_descent_file_name(src_path, src_file_name, descent)
        if not descent_file_name:
            raise FileNotFoundError(f'{src_path}/{src_file_name} ({descent})')
        return descent_path, descent_file_name

    @classmethod
    def list_descent_dir(cls, src_dir, path, descent):
        _index = {}
        result = []
        _dir = os.path.join(src_dir, path)
        entries = os.listdir(_dir)
        for entry in entries:
            full_path = os.path.join(_dir, entry)
            if os.path.isdir(full_path):
                result.append(entry)
            else:
                name: list = entry.split('.')
                name.pop(-2)
                entry_without_descent = '.'.join(name)
                if entry_without_descent not in _index:
                    _index[entry_without_descent] = 1
                    result.append(entry_without_descent)
        return result
