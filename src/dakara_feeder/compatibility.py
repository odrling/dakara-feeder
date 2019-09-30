import sys


# create ModuleNotFoundError error class for Python < 3.6
if sys.version_info.minor < 6:

    class ModuleNotFoundError(ImportError):
        pass
