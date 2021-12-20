import PyInstaller.__main__

from v8unpack import __version__
# from PyInstaller.utils.hooks import collect_submodules

_version = __version__.split('.')

# modules = ' '.join(collect_submodules('v8unpack'))

PyInstaller.__main__.run([
    'source.py',
    '--onefile',
    # '-n', f'v8unpack_{"_".join(_version[:-1])}',
    '-n', 'v8unpack',
    # '--hidden-import', modules,
    '--collect-submodules', 'v8unpack',
    '--collect-submodules', 'v8unpack.MetaObject',
    '--collect-submodules', 'v8unpack.MetaDataObject',
    '--distpath', '.'
])
