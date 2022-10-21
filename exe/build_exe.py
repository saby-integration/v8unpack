import PyInstaller.__main__

# from v8unpack.version import __version__
# from PyInstaller.utils.hooks import collect_submodules

# _version = __version__.split('.')

# modules = ' '.join(collect_submodules('v8unpack'))

PyInstaller.__main__.run([
    'source.py',
    '--onefile',
    '-n', 'v8unpack',
    # '--hidden-import', modules,
    '--collect-all', 'v8unpack',
    '--hidden-import', 'tqdm',
    '--hidden-import', 'os',
    '--distpath', '.'
])
