import sys

from .index import update_index
from .v8unpack import main, extract, extract_all, build, build_all, update_index, update_index_all
from .cf_patcher import CfPatcher
from .cf_file import CfFile

if __name__ == '__main__':
    sys.exit(main())
