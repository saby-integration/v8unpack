import json
import os
import shutil
from codecs import BOM_UTF8, BOM_UTF16_BE, BOM_UTF16_LE, BOM_UTF32_BE, BOM_UTF32_LE
from multiprocessing import Pool, cpu_count

from .ext_exception import ExtException


def json_read(path, file_name):
    _path = os.path.join(path, file_name)
    with open(_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def json_write(data, path, file_name):
    _path = os.path.join(path, file_name)
    os.makedirs(path, exist_ok=True)
    with open(_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def txt_read(path, file_name, encoding='utf-8-sig'):
    return txt_read_detect_encoding(path, file_name, encoding=encoding)[0]


def txt_read_detect_encoding(path, file_name, encoding='utf-8'):
    _path = os.path.join(path, file_name)
    if encoding is None:
        encoding = detect_by_bom(_path, 'utf-8')
    with open(_path, 'r', encoding=encoding) as file:
        return file.read(), encoding


def txt_write(data, path, file_name, encoding='utf-8'):
    if data is None:
        return
    _path = os.path.join(path, file_name)
    os.makedirs(path, exist_ok=True)
    with open(_path, 'w', encoding=encoding) as file:
        file.write(data)


def bin_write(data, path, file_name):
    _path = os.path.join(path, file_name)
    os.makedirs(path, exist_ok=True)
    with open(_path, 'wb') as file:
        file.write(data)


def bin_read(path, file_name):
    _path = os.path.join(path, file_name)
    with open(_path, 'rb') as file:
        return file.read()


def decode_header(obj: dict, header: list):
    obj['uuid'] = header[1][2]
    obj['name'] = str_decode(header[2])
    obj['name2'] = {}
    count_locale = int(header[3][0])
    for i in range(count_locale):
        obj['name2'][str_decode(header[3][i * 2 + 1])] = str_decode(header[3][i * 2 + 2])
    obj['comment'] = str_decode(header[4])
    obj['h1_0'] = header[1][0]
    obj['h0'] = header[0]
    obj['h5'] = header[5:]


def clear_dir(path: str) -> None:
    shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path, exist_ok=True)


def str_encode(data: str) -> str:
    return f'"{data}"'


def encode_name2(header: dict):
    result = [str(len(header['name2']))]
    for elem in header['name2']:
        result.append(str_encode(elem))
        result.append(str_encode(header['name2'][elem]))
    return result


def str_decode(data: str) -> str:
    return data[1:-1]


def get_pool(*, pool: Pool = None, processes=None) -> Pool:
    if pool is not None:
        return pool
    if processes is None:
        processes = cpu_count()
    return Pool(processes=processes)


def close_pool(local_pool: Pool, pool: Pool = None) -> None:
    if pool is None:
        local_pool.close()
        local_pool.join()


def run_in_pool(method, list_args, pool=None):
    _pool = get_pool(pool=pool)
    # msg = f'pool {method}({len(list_args)})'
    try:
        result = _pool.starmap(method, list_args)
    except Exception as err:
        close_pool(_pool, pool)
        raise ExtException(parent=err, detail=method, action='run_in_pool') from err
    close_pool(_pool, pool)
    return result


def list_merge(*args):
    result = []
    for lst in args:
        if lst:
            result.extend(lst)
    return result


def get_class_metadata_object(name):
    return get_class(f'v8unpack.MetaDataObject.{name}.{name}')


def get_class(kls):
    try:
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m
    except ImportError as e:
        # ошибки в классе  или нет файла
        raise ImportError(f'get_class({kls}: {str(e)}')
    except AttributeError as e:
        # Нет такого класса
        raise AttributeError(f'get_class({kls}: {str(e)}')
    except Exception as e:
        # ошибки в классе
        raise Exception(f'get_class({kls}: {str(e)}')


def detect_by_bom(path, default=None):
    boms = (
        ('utf-8-sig', BOM_UTF8),
        ('utf-32', BOM_UTF32_LE),
        ('utf-32', BOM_UTF32_BE),
        ('utf-16', BOM_UTF16_LE),
        ('utf-16', BOM_UTF16_BE),
    )

    with open(path, 'rb') as f:
        raw = f.read(4)  # will read less if the file is smaller
    for enc, bom in boms:
        if raw.startswith(bom):
            return enc
    return default


def str_time(value, _format='%H:%M:%S.%f'):
    return value.strftime(_format)


def get_extension_from_comment(comment: str) -> str:
    comment = comment.strip()
    if comment:
        return comment.split(" ")[-1]
    return "bin"


def check_version(v8_version: str, src_version: str) -> None:
    _v8 = v8_version.split(".")
    _src = src_version.split(".")
    if len(_v8) != 3:
        raise AssertionError(f'Не правильный номер версии v8unpack "{v8_version}"')
    if len(_src) != 3:
        raise AssertionError(f'Не правильная версия исходников "{src_version}"')
    if (int(_v8[0]), int(_v8[1])) != (int(_src[0]), int(_src[1])):
        raise AssertionError("Версия исходников {_src[0]}.{_src[1]} не соответствует версии v8unpack {_v8[0]}.{_v8[1]}")


def get_descent_file_name(file_name, descent):
    name: list = file_name.split('.')
    name.insert(-1, str(descent))
    return '.'.join(name)


def get_near_descent_file_name(path, file_name, descent):
    name: list = file_name.split('.')
    startswith = '.'.join(name[0:-1])
    endswith = name[-1]
    size = len(name)
    try:
        entities = os.listdir(path)
    except FileNotFoundError:
        os.makedirs(path, exist_ok=True)
        entities = []
    descents = []
    for entity in entities:
        if entity.startswith(startswith) and entity.endswith(endswith):
            _entity = entity.split('.')
            if len(_entity) - 1 != size:
                continue
            full_path = os.path.join(path, entity)
            if os.path.isfile(full_path):
                try:
                    descents.append(int(_entity[-2]))
                except ValueError:  # если во втором разряде не число, значит не наш вариант
                    pass
    if not descents:
        return '', ''
    descents = sorted(descents, reverse=True, key=lambda x: 0 if x > descent else x)
    if descents[0] > descent:
        return '', ''
    return path, f'{startswith}.{descents[0]}.{endswith}'
