import os
import shutil

from .file_organizer import FileOrganizer


class FileOrganizerCE(FileOrganizer):

    @classmethod
    def _unpack_file(cls, src_path, src_file_name, dest_path, dest_file_name, descent=None):
        _src_path = os.path.join(src_path, src_file_name)
        _dest_path = os.path.join(dest_path, dest_file_name)
        shutil.copy(_src_path, _dest_path)

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
