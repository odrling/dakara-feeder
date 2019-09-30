import importlib
import inspect
import logging
import os
import sys
from contextlib import contextmanager

from dakara_base.exceptions import DakaraError

from dakara_feeder.song import BaseSong


logger = logging.getLogger(__name__)


def get_custom_song(class_module_name):
    """Get the customized Song class

    Args:
        class_module_name (str): Python name of the custom Song class to import. It
            can designate a class in a module, or a module. In this case,
            the guessed class name is "Song".

    Returns:
        class: Customized Song class.
    """
    custom_object = import_custom_object(class_module_name)

    # if the custom object is a module, get default "Song" class
    if inspect.ismodule(custom_object):
        try:
            custom_class = getattr(custom_object, "Song")

        except AttributeError as error:
            raise InvalidObjectModuleNameError(
                "Cannot find default class Song in module {}".format(
                    custom_object.__name__
                )
            ) from error

        # append ".Song" to make the class module name equal to the actual
        # module name of the class
        class_module_name += ".Song"

    else:
        custom_class = custom_object

    # check the custom class is a class
    if not inspect.isclass(custom_class):
        raise InvalidObjectTypeError("{} is not a class".format(class_module_name))

    # check the custom Song inherits from default Song
    if not issubclass(custom_class, BaseSong):
        raise InvalidObjectTypeError(
            "{} is not a Song subclass".format(class_module_name)
        )

    logger.info("Using custom Song class: {}".format(class_module_name))

    return custom_class


@contextmanager
def current_dir_in_path():
    """Temporarily add current directory to top of the Python path

    Python path is reseted to its initial state when leaving the context
    manager.
    """
    # get copy of system path
    old_path_list = sys.path.copy()

    try:
        # prepend the current dir in path
        sys.path.insert(0, os.getcwd())
        yield None

    finally:
        # restore system path
        sys.path = old_path_list


def import_custom_object(object_module_name):
    """Import a custom object from a given module name

    Args:
        object_module_name (str): Python name of the custom object to import.
            It can designate a module, a class, a function or anything.

    Returns:
        type: Imported object.
    """
    object_module_name_list = object_module_name.split(".")

    # let's try to find module in object module name
    for length in range(len(object_module_name_list), 0, -1):
        module_name = ".".join(object_module_name_list[:length])

        # try to import the module
        try:
            with current_dir_in_path():
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
    custom_object = module
    try:
        for attr in object_module_name_list[length:]:
            custom_object = getattr(custom_object, attr)
            module_name += ".{}".format(attr)

    except AttributeError as error:
        raise InvalidObjectModuleNameError(
            "No module or object {} found in {}".format(attr, module_name)
        ) from error

    return custom_object


class InvalidObjectModuleNameError(DakaraError, ImportError, AttributeError):
    """Error when the object requested does not exist
    """


class InvalidObjectTypeError(DakaraError):
    """Error when the object type is unexpected
    """
