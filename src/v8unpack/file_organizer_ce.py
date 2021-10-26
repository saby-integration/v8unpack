import os
import shutil

from .file_organizer import FileOrganizer
from . import helper


class FileOrganizerCE(FileOrganizer):

    @classmethod
    def _unpack_file(cls, src_path, src_file_name, dest_path, dest_file_name, descent=None):
        src_full_path = os.path.join(src_path, src_file_name)

        descent_file_name = helper.get_descent_file_name(dest_file_name, descent)
        descent_full_dest_path = os.path.join(dest_path, descent_file_name)

        if not os.path.isfile(descent_full_dest_path):  # если нет файла нужной версии
            near_descent_path, near_descent_file_name = helper.get_near_descent_file_name(dest_path, dest_file_name, descent)
            if near_descent_file_name:  # нашли файл младшей версии
                with open(os.path.join(near_descent_path, near_descent_file_name), 'rb') as near_file:
                    with open(src_full_path, 'rb') as src_file:
                        near_data = near_file.read()
                        src_data = src_file.read()
                        if near_data == src_data:  # если файл не менялся, ничего с ним не делаем
                            return

        # если есть файл нашей версии или новый файл отличается от старого, или старого файла нет
        # сохраняем файл с номером текущей версии
        # считаем, что общие изменения должны делаться на минимальной версии
        shutil.copy(src_full_path, descent_full_dest_path)

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
