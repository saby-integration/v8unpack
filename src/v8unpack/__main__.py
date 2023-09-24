import sys
from multiprocessing import freeze_support

from v8unpack import main

if __name__ == '__main__':
    freeze_support()
    sys.exit(main())
