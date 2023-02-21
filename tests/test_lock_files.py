import unittest
from v8unpack import helper
import os
import time
from multiprocessing import Pool, Manager, Lock


def test_write(params):
    data, path, file_name = params
    _path = os.path.join(path, file_name)
    os.makedirs(path, exist_ok=True)
    with open(_path, 'w', encoding='utf-8') as file:
        time.sleep(1)
        print(data)
        file.write(data)
    return data


class TestLockFiles(unittest.TestCase):
    def test_multi_write(self):
        pool = helper.get_pool(processes=3)
        tasks = []
        path = os.path.join(os.path.dirname(__file__), 'tmp')
        for i in range(30):
            tasks.append([f'test{i}', path, 'test.txt'])

        with pool:
            res = pool.map(test_write, tasks, chunksize=10)
        pass