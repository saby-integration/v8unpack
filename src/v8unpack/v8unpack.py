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
from .index import update_index
from . import __version__


def extract(in_filename: str, out_dir_name: str, *, temp_dir=None, index=None, version=None):
    begin0 = datetime.now()
    print(f"v8unpack {__version__}")
    print(f"{helper.str_time(begin0)} Начали        ", end='')

    helper.clear_dir(os.path.normpath(out_dir_name))
    clear_temp_dir = False
    if temp_dir is None:
        clear_temp_dir = True
        temp_dir = tempfile.mkdtemp()
    helper.clear_dir(os.path.normpath(temp_dir))

    stage1_dir = os.path.join(temp_dir, 'decode_stage_1')
    stage2_dir = os.path.join(temp_dir, 'decode_stage_2')
    stage3_dir = os.path.join(temp_dir, 'decode_stage_3')

    if index:
        try:
            with open(index, 'r', encoding='utf-8') as f:
                index = json.load(f)
        except FileNotFoundError:
            index = None

    pool = helper.get_pool()

    begin1 = datetime.now()
    print(f" - {begin1 - begin0}\n{helper.str_time(begin1)} Распаковываем ", end='')
    container_extract(in_filename, stage1_dir)

    begin2 = datetime.now()
    print(f" - {begin2 - begin1}\n{helper.str_time(begin2)} Конвертируем  ", end='')
    json_decode(stage1_dir, stage2_dir, pool=pool)

    begin3 = datetime.now()
    print(f" - {begin3 - begin2}\n{helper.str_time(begin0)} Раcшифровываем", end='')
    decode(stage2_dir, stage3_dir, pool=pool, version=version)

    begin4 = datetime.now()
    print(f" - {begin4 - begin3}\n{helper.str_time(begin0)} Организуем    ", end='')
    FileOrganizer.unpack(stage3_dir, out_dir_name, pool=pool, index=index)

    end = datetime.now()
    print(f" - {end - begin4}\n{helper.str_time(end)} Готово         - {end - begin0}")

    helper.close_pool(pool)
    if clear_temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)


def build(in_dir_name: str, out_file_name: str, *, temp_dir=None, index=None, version='803'):
    begin0 = datetime.now()
    print(f"v8unpack {__version__}")
    print(f"{helper.str_time(begin0)} Начали        ", end='')
    clear_temp_dir = False
    if temp_dir is None:
        clear_temp_dir = True
        temp_dir = tempfile.mkdtemp()
    helper.clear_dir(os.path.normpath(temp_dir))

    encode_dir_stage1 = os.path.join(temp_dir, 'encode_stage_1')
    encode_dir_stage2 = os.path.join(temp_dir, 'encode_stage_2')
    encode_dir_stage3 = os.path.join(temp_dir, 'encode_stage_3')

    pool = helper.get_pool()

    if index:
        try:
            with open(index, 'r', encoding='utf-8') as f:
                index = json.load(f)
        except FileNotFoundError:
            index = None

    begin1 = datetime.now()
    print(f" - {begin1 - begin0}\n{helper.str_time(begin1)} Собираем      ", end='')
    FileOrganizer.pack(in_dir_name, encode_dir_stage3, pool=pool, index=index)

    begin2 = datetime.now()
    print(f" - {begin2 - begin1}\n{helper.str_time(begin2)} Зашифровываем ", end='')
    encode(encode_dir_stage3, encode_dir_stage2, version=version, pool=pool)

    begin3 = datetime.now()
    print(f" - {begin3 - begin2}\n{helper.str_time(begin0)} Конвертируем  ", end='')
    json_encode(encode_dir_stage2, encode_dir_stage1, pool=pool)

    begin4 = datetime.now()
    print(f" - {begin4 - begin3}\n{helper.str_time(begin0)} Запаковываем  ", end='')
    container_build(encode_dir_stage1, out_file_name)

    end = datetime.now()
    print(f" - {end - begin4}\n{helper.str_time(end)} Готово         - {end - begin0}")

    helper.close_pool(pool)
    if clear_temp_dir:
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
    group.add_argument('-I', nargs=1, metavar='src',
                       help='сформировать index, где '
                            'src - путь до папки с исходниками'
                       )
    parser.add_argument('--temp', help='путь до временной папки')
    parser.add_argument('--core', help='название общей папки добавляемой в индекс по умолчанию')
    parser.add_argument('--index', help='путь до json файла с словарем копирования,'
                                        'структура файла: {путь исходника: путь общей папки}')
    parser.add_argument('--version', default='803',
                        help="версия сборки 801/802/803, по умолчанию 803, "
                             " для сборки и разборки расширений указывается версия режима совместимости "
                             "например для 8.3.6 это 80306, подробности в документации на github")

    if len(sys.argv) == 1:
        parser.print_help()
        return 1

    args = parser.parse_args()

    if args.E is not None:
        extract(args.E[0], args.E[1], index=args.index, temp_dir=args.temp)

    if args.B is not None:
        build(args.B[0], args.B[1], index=args.index, temp_dir=args.temp, version=args.version)

    if args.I is not None:
        update_index(args.I[0], args.index, args.core)


if __name__ == '__main__':
    sys.exit(main())
