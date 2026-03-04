import sys
import v8unpack
from multiprocessing import freeze_support

if __name__ == '__main__':
    freeze_support()
    sys.exit(v8unpack.main())
