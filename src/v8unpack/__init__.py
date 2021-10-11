__version__ = '0.4.1'

from .v8unpack import main, extract, build
from .index import update_index
import sys

if __name__ == '__main__':
    sys.exit(main())
