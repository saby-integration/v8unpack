import PyInstaller.__main__

PyInstaller.__main__.run([
    'source.py',
    '--onefile',
    '-n', 'v8unpack',
    '--collect-all', 'v8unpack',
    '--hidden-import', 'tqdm',
    '--hidden-import', 'os',
    '--distpath', '.'
])
