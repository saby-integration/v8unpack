py -m build

py -m pip install -e .

pyinstaller ./exe/source.py --onefile --name v8unpack --distpath ./exe/ --collect-submodules v8unpack --collect-submodules v8unpack.MetaObject --collect-submodules v8unpack.MetaDataObject