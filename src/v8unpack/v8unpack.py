from datetime import datetime
import argparse
import sys
import os
import tempfile
import shutil
import json
from .container_reader import extract as container_extract
from .container_writer import build as container_build
from .json_container_decoder import json_decode, json_encode
from .decoder import decode, encode
from .file_organizer import FileOrganizer
from . import helper
from .index import create_index
from . import __version__


def extract(in_filename, out_dir_name, *, temp_dir=None, index=None):
    begin0 = datetime.now()
    print(f"v8unpack {__version__}")
    print(f"{helper.str_time(begin0)} Начали        ", end='')

    helper.clear_dir(os.path.normpath(out_dir_name))
    if temp_dir is None:
        temp_dir = tempfile.mkdtemp()
        helper.clear_dir(os.path.normpath(temp_dir))

    stage1_dir = os.path.join(temp_dir, 'decode_stage_1')
    stage2_dir = os.path.join(temp_dir, 'decode_stage_2')
    stage3_dir = os.path.join(temp_dir, 'decode_stage_3')

    if index:
        with open(index, 'r', encoding='utf-8') as f:
            index = json.load(f)

    pool = helper.get_pool()

    begin1 = datetime.now()
    print(f" - {begin1 - begin0}\n{helper.str_time(begin1)} Распаковываем ", end='')
    container_extract(in_filename, stage1_dir)

    begin2 = datetime.now()
    print(f" - {begin2 - begin1}\n{helper.str_time(begin2)} Конвертируем  ", end='')
    json_decode(stage1_dir, stage2_dir, pool=pool)

    begin3 = datetime.now()
    print(f" - {begin3 - begin2}\n{helper.str_time(begin0)} Раcшифровываем", end='')
    decode(stage2_dir, stage3_dir, pool=pool)

    begin4 = datetime.now()
    print(f" - {begin4 - begin3}\n{helper.str_time(begin0)} Организуем    ", end='')
    FileOrganizer.unpack(stage3_dir, out_dir_name, pool=pool, index=index)

    end = datetime.now()
    print(f" - {end - begin4}\n{helper.str_time(end)} Готово         - {end - begin0}")

    helper.close_pool(pool)
    shutil.rmtree(temp_dir, ignore_errors=True)


def build(folder, file, *, temp_dir=None, index=None, version='83'):
    begin0 = datetime.now()
    print(f"v8unpack {__version__}")
    print(f"{helper.str_time(begin0)} Начали        ", end='')
    if temp_dir is None:
        temp_dir = tempfile.mkdtemp()
        helper.clear_dir(os.path.normpath(temp_dir))

    encode_dir_stage1 = os.path.join(temp_dir, 'encode_stage_1')
    encode_dir_stage2 = os.path.join(temp_dir, 'encode_stage_2')
    encode_dir_stage3 = os.path.join(temp_dir, 'encode_stage_3')

    pool = helper.get_pool()

    if index:
        with open(index, 'r', encoding='utf-8') as f:
            index = json.load(f)

    begin1 = datetime.now()
    print(f" - {begin1 - begin0}\n{helper.str_time(begin1)} Собираем      ", end='')
    FileOrganizer.pack(folder, encode_dir_stage3, pool=pool, index=index)

    begin2 = datetime.now()
    print(f" - {begin2 - begin1}\n{helper.str_time(begin2)} Зашифровываем ", end='')
    encode(encode_dir_stage3, encode_dir_stage2, version=version, pool=pool)

    begin3 = datetime.now()
    print(f" - {begin3 - begin2}\n{helper.str_time(begin0)} Конвертируем  ", end='')
    json_encode(encode_dir_stage2, encode_dir_stage1, pool=pool)

    begin4 = datetime.now()
    print(f" - {begin4 - begin3}\n{helper.str_time(begin0)} Запаковываем  ", end='')
    container_build(encode_dir_stage1, file)

    end = datetime.now()
    print(f" - {end - begin4}\n{helper.str_time(end)} Готово         - {end - begin0}")

    helper.close_pool(pool)
    shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(
        prog=f'v8unpack {__version__}',
        description='Распаковка и сборка бинарных файлов 1С'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-E', nargs=2, metavar=('file', 'src'),
                       help='разобрать файл 1С, где '
                            'file - путь до бинарного файла, '
                            'src -  папка куда будут помещены исходники')
    group.add_argument('-B', nargs=2, metavar=('src', 'file'),
                       help='собрать файл 1С, где '
                            'src - путь до папки с исходниками, '
                            'file - путь до бинарного файла')
    group.add_argument('-I', nargs=3, metavar=('file', 'src', 'dest'),
                       help='сформировать index, где '
                            'file - путь до файла с индексом, '
                            'src - путь до папки с исходниками, '
                            'dest - путь до общей папки')
    parser.add_argument('--temp', help='путь до временной папки')
    parser.add_argument('--index', help='путь до json файла с словарем копирования,'
                                        'структура файла: {путь исходника: путь общей папки}')
    parser.add_argument('--version', default='83', help="версия сборки 81/82/83,"
                                                        " по умолчанию 83, "
                                                        "для разборки не требуется")

    if len(sys.argv) == 1:
        parser.print_help()
        return 1

    args = parser.parse_args()

    if args.E is not None:
        extract(args.E[0], args.E[1], index=args.index, temp_dir=args.temp)

    if args.B is not None:
        build(args.B[0], args.B[1], index=args.index, temp_dir=args.temp, version=args.version)

    if args.I is not None:
        create_index(args.I[0], args.I[1], args.I[2])


if __name__ == '__main__':
    sys.exit(main())
