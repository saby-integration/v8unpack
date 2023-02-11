import json
import copy
import os
import shutil
import time
import uuid
from codecs import BOM_UTF8, BOM_UTF16_BE, BOM_UTF16_LE, BOM_UTF32_BE, BOM_UTF32_LE
from multiprocessing import Pool, cpu_count

from tqdm.auto import tqdm

from .ext_exception import ExtException
from .json_container_decoder import JsonContainerDecoder, BigBase64


def brace_file_read(path, file_name):
    _path = os.path.join(path, file_name)
    try:
        for code_page in ['utf-8-sig', 'windows-1251']:
            try:
                with open(_path, 'r', encoding=code_page) as file:
                    decoder = JsonContainerDecoder(src_dir=path, file_name=file_name)
                    data = decoder.decode_file(file)
                    return data
            except UnicodeDecodeError:
                continue
        raise ExtException(message=f'Unknown code page in file {file_name}')
    except (BigBase64, FileNotFoundError) as err:
        raise err from err
    except Exception as err:
        raise ExtException(parent=err, message='Ошибка чтения', detail=f'{err} в файле ({_path})')


def brace_file_write(data, path, file_name):
    _path = os.path.join(path, file_name)
    makedirs(path, exist_ok=True)
    try:
        with open(_path, 'w', encoding='utf-8') as file:
            decoder = JsonContainerDecoder(src_dir=path, file_name=file_name)
            raw_data = decoder.encode_root_object(data)
            decoder.write_data(path, file_name, raw_data)
    except Exception as err:
        raise ExtException(message='Ошибка записи', detail=f'{err} в файле ({_path})')


def json_read(path, file_name):
    _path = os.path.join(path, file_name)
    try:
        with open(_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError as err:
        raise err from err
    except Exception as err:
        raise ExtException(message='Ошибка чтения', detail=f'{err} в файле ({_path})')


def json_write(data, path, file_name):
    _path = os.path.join(path, file_name)
    makedirs(path, exist_ok=True)
    try:
        with open(_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except Exception as err:
        raise ExtException(message='Ошибка записи', detail=f'{err} в файле ({_path})')


def txt_read(path, file_name, encoding='utf-8-sig'):
    try:
        return txt_read_detect_encoding(path, file_name, encoding=encoding)[0]
    except FileNotFoundError as err:
        raise err from err
    except Exception as err:
        raise ExtException(message='Ошибка чтения', detail=f'{err} в файле ({file_name})')


def txt_read_detect_encoding(path, file_name, encoding='utf-8'):
    _path = os.path.join(path, file_name)
    if encoding is None:
        encoding = detect_by_bom(_path, 'utf-8')
    with open(_path, 'r', encoding=encoding) as file:
        return file.read(), encoding


def txt_write(data, path, file_name, encoding='utf-8'):
    try:
        if data is None:
            return
        _path = os.path.join(path, file_name)
        makedirs(path, exist_ok=True)
        for i in range(3):
            try:
                with open(_path, 'w', encoding=encoding) as file:
                    file.write(data)
                return
            except PermissionError:
                time.sleep(0.5)
        raise PermissionError(_path)
    except Exception as err:
        raise ExtException(message='Ошибка записи файла', detail=f'{err} в файле {path}')


def bin_write(data, path, file_name):
    _path = os.path.join(path, file_name)
    makedirs(path, exist_ok=True)
    with open(_path, 'wb') as file:
        file.write(data)


def bin_read(path, file_name):
    _path = os.path.join(path, file_name)
    with open(_path, 'rb') as file:
        return file.read()


def decode_header(obj: dict, header: list):
    try:
        obj['uuid'] = header[1][2]
        uuid.UUID(obj['uuid'])

    except (ValueError, IndexError):
        raise ValueError('Заголовок определен не верно')

    obj['name'] = str_decode(header[2])
    obj['name2'] = {}
    count_locale = int(header[3][0])
    for i in range(count_locale):
        obj['name2'][str_decode(header[3][i * 2 + 1])] = str_decode(header[3][i * 2 + 2])
    comment = str_decode(header[4]).split(';')[0]  # удаляем имя файла и номер версии которую добавляем при сборке
    header[4] = str_encode(comment)
    obj['comment'] = comment
    obj['h1_0'] = header[1][0]
    obj['h0'] = header[0]
    obj['h5'] = header[5:]


def clear_dir(path: str) -> None:
    shutil.rmtree(path, ignore_errors=True)
    makedirs(path, exist_ok=True)


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
        processes = max(cpu_count() - 2, 1)  # чтобы система совсем не висла
    return Pool(processes)


def close_pool(local_pool: Pool, pool: Pool = None) -> None:
    if pool is None:
        local_pool.close()
        local_pool.join()


def run_in_pool(method, list_args, pool=None, title=None, need_result=False):
    _pool = get_pool(pool=pool)
    result = []
    # msg = f'pool {method}({len(list_args)})'
    try:
        with tqdm(desc=title, total=len(list_args)) as pbar:
            for _res in _pool.imap_unordered(method, list_args, chunksize=1):
                if need_result and _res:
                    result.extend(_res)
                pbar.update()
    except ExtException as err:
        raise ExtException(
            parent=err,
            action=f'run_in_pool {method.__qualname__}') from err
    # except Exception as err:
    #     raise ExtException(parent=err, detail=f'{method.__qualname__ {err.message}' action=f'run_in_pool {method.__qualname__}') from err
    finally:
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
    res = 'bin'
    if comment:
        ext = comment.split(" ")[-1]
        if len(ext) < 6 and ext.isalnum():
            return ext
    return res


def check_version(v8_version: str, src_version: str) -> None:
    _v8 = v8_version.split(".")
    _src = src_version.split(".")
    if len(_v8) != 3:
        raise AssertionError(f'Не правильный номер версии v8unpack "{v8_version}"')
    if len(_src) != 3:
        raise AssertionError(f'Не правильная версия исходников "{src_version}"')
    if (int(_v8[0]), int(_v8[1])) != (int(_src[0]), int(_src[1])):
        raise AssertionError(
            f"Версия исходников {_src[0]}.{_src[1]} не соответствует версии v8unpack {_v8[0]}.{_v8[1]}")


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
        makedirs(path, exist_ok=True)
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


def remove_descent_from_filename(file_name):
    _name = file_name.split('.')
    try:
        if len(_name) < 3:
            return file_name
        _descent = _name.pop(-2)
        if str(int(_descent)) == _descent:
            return '.'.join(_name)
    except Exception:
        return file_name


def makedirs(name, exist_ok=False):
    for i in range(3):
        try:
            os.makedirs(name, exist_ok=exist_ok)
            return
        except PermissionError:
            time.sleep(0.5)
    raise PermissionError(name)


class FuckingBrackets(ExtException):
    pass


def update_dict(*args):
    size = len(args)
    if size == 1:
        return _update_dict({}, args[0])
    elif size > 1:
        result = args[0]
        for i in range(size - 1):
            result = _update_dict(result, args[i + 1])
        return result

def _update_dict(base, new, _path=''):
    if not new:
        return base
    for element in new:
        try:
            if element in base and base[element] is not None:
                if isinstance(new[element], dict):
                    if isinstance(base[element], dict):
                        base[element] = _update_dict(base[element], new[element], f'{_path}.{element}')
                    else:
                        raise ExtException(
                            message='type mismatch',
                            detail=f'{type(base[element])} in {_path}.{element}',
                            dump={'value': str(base[element])}
                        )
                elif isinstance(new[element], list):
                    raise NotImplementedError('update list')
                    # base[element] = ArrayHelper.unique_extend(base[element], new[element])
                else:
                    base[element] = new[element]
            else:
                try:
                    base[element] = copy.deepcopy(new[element])
                except TypeError as e:
                    if not base:
                        base = {
                            element: copy.deepcopy(new[element])
                        }
                    else:
                        raise NotImplementedError()
        except ExtException as err:
            raise ExtException(parent=err) from err
        except Exception as err:
            raise ExtException(
                parent=err,
                action='Helper.update_dict',
                detail='{0}({1})'.format(err, _path),
                dump={
                    'element': element,
                    'message': str(err)
                })
    return base