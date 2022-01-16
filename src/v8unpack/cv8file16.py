from .cv8file import FileHeader, BlockHeader, CV8File


class FileHeader64(FileHeader):
    fmt = '1Q1i1i1i'
    end_marker = 0xffffffffffffffff


class BlockHeader64(BlockHeader):
    fmt = '1c1c16s1c16s1c16s1c1c1c'


class CV8File16(CV8File):
    header_offset = 0x1359
    class_file_header = FileHeader64
    class_block_header = BlockHeader64


def extract(filename, dest_dir, deflate=True, recursive=True):
    with open(filename, 'rb') as file:
        if CV8File16.is_v8_file(file):
            CV8File16.parse(file, dest_dir, deflate=True, recursive=True)
        if CV8File.is_v8_file(file):
            CV8File16.parse(file, dest_dir, deflate=True, recursive=True)
        raise Exception('Not v8file')
