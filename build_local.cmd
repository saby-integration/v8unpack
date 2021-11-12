py -m build

py -m pip install -e .

pyinstaller /exe/source.py --onefile --name v8unpack --distpath /exe/