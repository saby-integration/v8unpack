# -*- coding: utf-8 -*-
import os
import zlib
from datetime import datetime

from . import helper
from .container import Container, Container64
from .ext_exception import ExtException


def extract(filename, folder, deflate=True, recursive=True):
    """
    Распаковка контейнера. Сахар для ContainerReader

    :param filename: полное имя файла-контейнера
    :type filename: string
    :param folder: каталог назначения
    :type folder: string
    :param deflate: паспаковка
    :type deflate: boolean
    :param recursive: рекурсивно достаем все контейнеры
    :type recursive: boolean
    """
    begin = datetime.now()
    print(f'{"Распаковываем бинарник":30}:', end="")
    helper.clear_dir(folder)
    with open(filename, 'rb') as f:
        offset = 0
        container_index = 0
        while True:
            try:
                container = detect_format(f, offset)
                container.read(f, offset)
                container.extract(os.path.join(folder, str(container_index)), deflate, recursive)
                container_index += 1
                offset = container.size
                if offset == 0:
                    raise NotImplementedError()
            except Exception as err:
                break

    print(f"{datetime.now() - begin}")


def detect_format(f, offset):
    f.seek(offset)
    first = f.read(8)
    if first[0:4] == b'\xFF\xFF\xFF\x7F':
        return Container()
    elif first == b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF':
        return Container64()
    else:
        raise Exception('Файл не является контейнером')


def decompress_and_extract(src_folder, dest_folder, *, pool=None):
    helper.clear_dir(dest_folder)
    containers = os.listdir(src_folder)
    helper.clear_dir(dest_folder)
    tasks = []
    for container in containers:
        _src_folder = os.path.join(src_folder, container)
        _dest_folder = os.path.join(dest_folder, container)
        helper.clear_dir(_dest_folder)
        entries = os.listdir(_src_folder)
        for filename in entries:
            tasks.append([_src_folder, filename, _dest_folder])

    helper.run_in_pool(decompress_file_and_extract, tasks, pool=pool, title=f'{"Распаковываем контейнеры":30}')


def decompress_file_and_extract(params):
    src_folder, filename, dest_folder = params
    src_path = os.path.join(src_folder, filename)
    dest_path = os.path.join(dest_folder, filename)
    file_is_container = None

    # wbits = -15 т.к. у архивированных файлов нет заголовков
    decompressor = zlib.decompressobj(-15)
    try:
        with open(dest_path, 'wb') as dest:
            with open(src_path, 'rb') as src:
                while True:
                    buf = decompressor.unconsumed_tail
                    if buf == b'':
                        buf = src.read(8192)
                        if buf == b'':
                            break
                    data = decompressor.decompress(buf)
                    if file_is_container is None:
                        file_is_container = data[0:4] == b'\xFF\xFF\xFF\x7F'
                    if data == b'':
                        break
                    dest.write(data)

        # Каждый файл внутри контейнера может быть контейнером
        # Для проверки является ли файл контейнером проверим первые 4 бита
        # Способ проверки ненадежный - нужно придумать что-то другое

        if file_is_container:
            temp_filename = dest_path + ".temp"
            os.rename(dest_path, temp_filename)
            with open(temp_filename, 'rb') as f:
                container = Container()
                container.read(f)
                container.extract(dest_path, recursive=True)
            os.remove(temp_filename)

    except Exception as err:
        raise ExtException(
            parent=err, message="Ошибка при разархифировании контейнера",
            detail=f'{filename} ({err})')
