# -*- coding: utf-8 -*-
"""Управление файлом versions в .cf контейнерах 1С.

Файл versions содержит UUID v4 для каждого файла в контейнере.
Платформа 1С использует эти UUID как кеш при сравнении/объединении:
если UUID совпадает — содержимое не проверяется.

При модификации файлов через extract→patch→build файл versions
необходимо удалить, чтобы платформа при CompareCfg/MergeCfg
проверила содержимое всех объектов.

DumpCfg платформы заново генерирует versions при следующей выгрузке.
LoadCfg работает корректно и без versions.
"""
import os
import zlib


def compute_checksums(directory):
    """Вычислить CRC32 для всех файлов в директории.

    Returns:
        dict: {filename: crc32_int}
    """
    checksums = {}
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isdir(path):
            continue
        crc = 0
        with open(path, 'rb') as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                crc = zlib.crc32(chunk, crc)
        checksums[name] = crc & 0xffffffff
    return checksums


def invalidate_versions_if_changed(directory, old_checksums):
    """Удалить файл versions если какой-либо файл изменился.

    Сравнивает текущие CRC32 файлов с сохранёнными при extract.
    Если хотя бы один файл изменён — удаляет versions целиком.

    Платформа 1С при отсутствии versions сравнивает содержимое
    всех объектов напрямую. Это корректное поведение —
    DumpCfg заново сгенерирует versions.

    Args:
        directory: путь к распакованному контейнеру
        old_checksums: dict {filename: crc32} из compute_checksums() при extract
    """
    ver_path = os.path.join(directory, 'versions')
    if not os.path.exists(ver_path):
        return

    new_checksums = compute_checksums(directory)

    for name, old_crc in old_checksums.items():
        new_crc = new_checksums.get(name)
        if new_crc is not None and new_crc != old_crc:
            os.remove(ver_path)
            return

    # Новые файлы
    for name in new_checksums:
        if name not in old_checksums and name != 'versions':
            os.remove(ver_path)
            return
