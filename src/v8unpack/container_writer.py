# -*- coding: utf-8 -*-
import datetime
import os
import tempfile
from base64 import b64encode
from datetime import datetime
from hashlib import sha1

from tqdm.auto import tqdm

from . import helper
from .container import Container, Container64
from .container_doc import Document
from .json_container_decoder import JsonContainerDecoder


def build(src_dir, filename, nested=False):
    """
    Запаковывает каталог в контейнер включая вложенные каталоги.
    Сахар для ContainerWriter.

    :param src_dir: каталог с данными, запаковываемыми в контейнер
    :type src_dir: string
    :param filename: имя файла контейнера
    :type filename: string
    :param nested:
    :type nested: bool
    :param version: версия под которую собирается продукт
    :type version: string
    """
    begin = datetime.now()
    print(f'{"Запаковываем бинарник":30}:', end="")
    helper.makedirs(os.path.dirname(filename), exist_ok=True)

    containers = os.listdir(src_dir)
    _src_dir = containers[-1]
    containers_count = len(containers)
    if containers_count not in [1, 2]:
        raise NotImplementedError(f'Количество контейнеров {containers_count}')

    with open(filename, 'w+b') as f:
        _src_dir = os.path.join(src_dir, '0')
        container = Container()
        container.build(f, _src_dir, nested, offset=0)
        if containers_count == 2:
            _src_dir = os.path.join(src_dir, '1')
            container = Container64()
            container.build(f, _src_dir, nested, offset=f.seek(0, os.SEEK_END))
    print(f" - {datetime.now() - begin}")


def calc_sha1(src_folder, dest_folder):
    entries = sorted(os.listdir(dest_folder))
    versions = []
    versions_file = ''
    for filename in entries:
        dest_path = os.path.join(dest_folder, filename)
        if filename == 'configinfo':
            versions_file = 'configinfo'
            continue

        with open(dest_path, 'rb') as file:
            data = file.read()
        versions.append(f'"{filename}"')
        versions.append(b64encode(sha1(data).digest()).decode())
    if not versions_file:
        return
    versions.insert(0, str(int(len(versions) / 2)))
    _versions = JsonContainerDecoder().encode_root_object([versions])

    src_path = os.path.join(src_folder, versions_file)
    dest_path = os.path.join(dest_folder, versions_file)

    with open(src_path, 'r+', encoding='utf-8') as file:
        data = file.read()
        data = data.replace('{____versions____}', _versions)
        file.seek(0)
        file.write(data)

    compress_and_build_simple_file(src_path, dest_path)
    pass


def compress_and_build_simple_file(src_path, dest_path):
    with open(dest_path, 'w+b') as dest_fd:
        with open(src_path, 'rb') as src_fd:
            Document.compress(src_fd, dest_fd)


def compress_and_build(src_dir, dest_dir, *, pool=None, nested=False):
    containers = os.listdir(src_dir)
    helper.clear_dir(dest_dir)
    for dir_name in containers:
        _src_dir = os.path.join(src_dir, dir_name)
        _dest_dir = os.path.join(dest_dir, dir_name)
        helper.clear_dir(_dest_dir)

        entries = sorted(os.listdir(_src_dir))

        with tqdm(desc=f'{"Архивируем контейнеры":30}', total=len(entries)) as pbar:
            for filename in entries:
                src_path = os.path.join(_src_dir, filename)
                dest_path = os.path.join(_dest_dir, filename)
                # add_entry(container, src_dir, filename)
                if os.path.isdir(src_path):
                    with open(dest_path, 'w+b') as dest_fd:
                        with tempfile.TemporaryFile() as tmp:
                            container = Container()
                            container.build(tmp, src_path, nested=True)
                            Document.compress(tmp, dest_fd)
                else:
                    compress_and_build_simple_file(src_path, dest_path)
                pbar.update()
            calc_sha1(_src_dir, _dest_dir)
