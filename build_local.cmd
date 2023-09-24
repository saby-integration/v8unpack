python -m build

python -m pip install -e .

pyinstaller ./exe/source.py --onefile --name v8unpack --distpath ./exe/ --collect-all v8unpack --hidden-import tqdm