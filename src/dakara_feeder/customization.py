"""Customize the Song class."""

import importlib
import inspect
import logging
import sys
from contextlib import contextmanager

from dakara_base.exceptions import DakaraError
from path import Path

from dakara_feeder.song import BaseSong

logger = logging.getLogger(__name__)


def get_custom_song(string, default_class_name="Song"):
    """Get the customized Song class.

    See also:
        `split_path_module` for the syntax of `string`.

    Args:
        string (str): Either name of a module or path to a file, containing a
            subclass of `dakara_feeder.song.BaseSong`. If the name of the class
            is not provided, then fallback to `default_class_name`.
        default_class_name (str): Default song class name to use.

    Returns:
        class: Customized Song class.

    Raises:
        InvalidObjectTypeError: If the designated object is not a class, or if
            it does not inherit from Song.
    """
    # import a file or a module
    file_path, module_name = split_path_module(string)
    if file_path is not None:
        custom_module = import_from_file(file_path)
        class_name = module_name or default_class_name
        separator = "::"

    elif module_name is not None:
        custom_module = import_from_module(module_name)
        class_name = default_class_name
        separator = "."

    else:
        raise InvalidSongConfigError("No song class file or module provided")

    # if the custom object is a module, get the song class
    if inspect.ismodule(custom_module):
        try:
            custom_class = getattr(custom_module, class_name)

        except AttributeError as error:
            raise InvalidObjectModuleNameError(
                "Cannot find class {} in module {}".format(
                    class_name, custom_module.__name__
                )
            ) from error

        # append song class name to the string
        string += separator + class_name

    else:
        custom_class = custom_module

    # check the custom class is a class
    if not inspect.isclass(custom_class):
        raise InvalidObjectTypeError("{} is not a class".format(string))

    # check the custom Song inherits from default Song
    if not issubclass(custom_class, BaseSong):
        raise InvalidObjectTypeError("{} is not a BaseSong subclass".format(string))

    logger.info("Using custom Song class: {}".format(string))

    return custom_class


def split_path_module(string):
    """Split a path and module string.

    The string is in the form `path::module`, each part is optional. The
    function splits the path from the module:

    >>> split_path_module("path/to/file.py::my.module")
    ... Path("path/to/file.py"), "my.module"
    >>> split_path_module("path/to/file.py")
    ... Path("path/to/file.py"), None
    >>> split_path_module("my.module")
    ... None, "my.module"

    Args:
        string (str): Path and module separated by `::`.

    Returns:
        tuple: Contains:

        1. path.Path: The path of the file;
        2. str: The module name.
    """
    # if nothing is given
    if not string:
        return None, None

    # both path and module given
    if "::" in string:
        path, module = string.split("::")

        # if no module is provided
        if not module:
            module = None

        return Path(path), module

    # only path given
    if ".py" in string:
        return Path(string), None

    # assume only module given
    return None, string


@contextmanager
def dir_in_path(directory):
    """Temporarily add a directory to the top of the Python path.

    Python path is reseted to its initial state when leaving the context
    manager.

    Args:
        directory (path.Path): Directory to add.
    """
    # get copy of system path
    old_path_list = sys.path.copy()

    try:
        # prepend the directory in path
        sys.path.insert(0, str(directory))
        yield None

    finally:
        # restore system path
        sys.path = old_path_list


def import_from_file(file_path):
    """Import a custom file as a module.

    Args:
        file_path (path.Path): Path to a Python file to import.

    Returns:
        type: Imported module.

    Raises:
        InvalidObjectModuleNameError: If the given module name cannot be found.
    """
    directory = file_path.parent
    module_name = file_path.stem

    try:
        with dir_in_path(directory):
            return importlib.import_module(module_name)

    except ImportError:
        raise InvalidObjectModuleNameError(
            "No module found from file {}".format(file_path)
        )


def import_from_module(object_module_name):
    """Import a custom object from a given module name.

    Args:
        object_module_name (str): Python name of the custom object to import.
            It can designate a module, a class, a function or anything.

    Returns:
        type: Imported object.

    Raises:
        InvalidObjectModuleNameError: If the given module name cannot be found.
    """
    object_module_name_list = object_module_name.split(".")

    # let's try to find module in object module name
    for length in range(len(object_module_name_list), 0, -1):
        module_name = ".".join(object_module_name_list[:length])

        # try to import the module
        try:
            module = importlib.import_module(module_name)

        # if not continue with parent module
        except ImportError:
            continue

        # if found
        break

    # if no module was found
    else:
        raise InvalidObjectModuleNameError("No module {} found".format(module_name))

    # get the custom object
    custom_module = module
    try:
        for attr in object_module_name_list[length:]:
            custom_module = getattr(custom_module, attr)
            module_name += ".{}".format(attr)

    except AttributeError as error:
        raise InvalidObjectModuleNameError(
            "No module or object {} found in {}".format(attr, module_name)
        ) from error

    return custom_module


class InvalidObjectModuleNameError(DakaraError, ImportError, AttributeError):
    """Error when the object requested does not exist."""


class InvalidObjectTypeError(DakaraError):
    """Error when the object type is unexpected."""


class InvalidSongConfigError(DakaraError):
    """Error when the config to get the Song file is wrong."""
