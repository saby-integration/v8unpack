import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime

from . import __version__
from . import helper
from .container_reader import extract as container_extract, decompress_and_extract
from .container_writer import build as container_build, compress_and_build
from .decoder import decode, encode
from .file_organizer import FileOrganizer
from .file_organizer_ce import FileOrganizerCE
from .index import update_index
from .json_container_decoder import json_decode, json_encode


def extract(in_filename: str, out_dir_name: str, *, temp_dir=None, index=None, version=None, descent=None):
    begin0 = datetime.now()
    print(f"v8unpack {__version__}")
    print(f"{helper.str_time(begin0)} Начали        ", end='')
    if descent is None:
        helper.clear_dir(os.path.normpath(out_dir_name))
    clear_temp_dir = False
    if temp_dir is None:
        clear_temp_dir = True
        temp_dir = tempfile.mkdtemp()
    helper.clear_dir(os.path.normpath(temp_dir))

    dir_stage0 = os.path.join(temp_dir, 'decode_stage_0')
    dir_stage1 = os.path.join(temp_dir, 'decode_stage_1')
    dir_stage2 = os.path.join(temp_dir, 'decode_stage_2')
    dir_stage3 = os.path.join(temp_dir, 'decode_stage_3')

    if index:
        try:
            with open(index, 'r', encoding='utf-8') as f:
                index = json.load(f)
        except FileNotFoundError:
            index = None

    pool = helper.get_pool()

    begin1 = datetime.now()
    print(f" - {begin1 - begin0}\n{helper.str_time(begin1)} Распаковываем ", end='')
    container_extract(in_filename, dir_stage0, False, False)
    decompress_and_extract(dir_stage0, dir_stage1, pool=pool)

    begin2 = datetime.now()
    print(f" - {begin2 - begin1}\n{helper.str_time(begin2)} Конвертируем  ", end='')
    json_decode(dir_stage1, dir_stage2, pool=pool)

    begin3 = datetime.now()
    print(f" - {begin3 - begin2}\n{helper.str_time(begin0)} Раcшифровываем", end='')
    decode(dir_stage2, dir_stage3, pool=pool, version=version)

    begin4 = datetime.now()
    print(f" - {begin4 - begin3}\n{helper.str_time(begin0)} Организуем    ", end='')
    if descent:
        FileOrganizerCE.unpack(dir_stage3, out_dir_name, pool=pool, index=index, descent=descent)
    else:
        FileOrganizer.unpack(dir_stage3, out_dir_name, pool=pool, index=index)

    end = datetime.now()
    print(f" - {end - begin4}\n{helper.str_time(end)} Готово         - {end - begin0}")

    helper.close_pool(pool)
    if clear_temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)


def build(in_dir_name: str, out_file_name: str, *, temp_dir=None, index=None,
          version='803', descent=None, release=None):
    begin0 = datetime.now()
    print(f"v8unpack {__version__}")
    print(f"{helper.str_time(begin0)} Начали        ", end='')
    clear_temp_dir = False
    if temp_dir is None:
        clear_temp_dir = True
        temp_dir = tempfile.mkdtemp()
    helper.clear_dir(os.path.normpath(temp_dir))

    dir_stage0 = os.path.join(temp_dir, 'encode_stage_0')
    dir_stage1 = os.path.join(temp_dir, 'encode_stage_1')
    dir_stage2 = os.path.join(temp_dir, 'encode_stage_2')
    dir_stage3 = os.path.join(temp_dir, 'encode_stage_3')

    pool = helper.get_pool()

    if index:
        try:
            with open(index, 'r', encoding='utf-8') as f:
                index = json.load(f)
        except FileNotFoundError:
            index = None

    begin1 = datetime.now()
    print(f" - {begin1 - begin0}\n{helper.str_time(begin1)} Собираем      ", end='')
    if descent:
        FileOrganizerCE.pack(in_dir_name, dir_stage3, pool=pool, index=index, descent=descent)
    else:
        FileOrganizer.pack(in_dir_name, dir_stage3, pool=pool, index=index)

    begin2 = datetime.now()
    print(f" - {begin2 - begin1}\n{helper.str_time(begin2)} Зашифровываем ", end='')
    encode(dir_stage3, dir_stage2, version=version, pool=pool, release=release)

    begin3 = datetime.now()
    print(f" - {begin3 - begin2}\n{helper.str_time(begin0)} Конвертируем  ", end='')
    json_encode(dir_stage2, dir_stage1, pool=pool)

    begin4 = datetime.now()
    print(f" - {begin4 - begin3}\n{helper.str_time(begin0)} Запаковываем  ", end='')
    compress_and_build(dir_stage1, dir_stage0, pool=pool)
    container_build(dir_stage0, out_file_name, True)

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
                        help="версия сборки, для сборки обработок указывается версия платформы 801/802/803, "
                             " для сборки расширений указывается версия режима совместимости, "
                             "например для 8.3.6 это 80306, подробности в документации на github")
    parser.add_argument('--descent',
                        help="включает режим наследования при сборке и разборке,"
                             "четырех значный формат 3.0.75.100 (не более 3 знаков на каждый разряд)"
                             "подробности в инструкции - раздел разработка расширений")
    parser.add_argument('--release',
                        help="номер версии собираемого продукта, "
                             "для обработки добавяется в функцию GetVersion модуля обработки, "
                             "для расширений устанавливается в соответствующий реквизит ")

    if len(sys.argv) == 1:
        parser.print_help()
        return 1

    args = parser.parse_args()
    descent = int(args.descent) if args.descent else None

    if args.E is not None:
        extract(os.path.abspath(args.E[0]), os.path.abspath(args.E[1]),
                index=args.index, temp_dir=args.temp, version=args.version, descent=descent)

    if args.B is not None:
        build(os.path.abspath(args.B[0]), os.path.abspath(args.B[1]),
              index=args.index, temp_dir=args.temp, version=args.version, descent=descent)

    if args.I is not None:
        update_index(args.I[0], args.index, args.core)


if __name__ == '__main__':
    sys.exit(main())
