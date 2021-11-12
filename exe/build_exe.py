import PyInstaller.__main__

from v8unpack import __version__

_version = __version__.split('.')

PyInstaller.__main__.run([
    'source.py',
    '--onefile',
    '-n',    f'v8unpack_{"_".join(_version[:-1])}',
    '--distpath', '.'
])
