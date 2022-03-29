"""Open JSON files safely."""

import json

from dakara_base.exceptions import DakaraError


def get_json_file_content(file_path, key=None):
    """Load content of the given JSON file.

    Args:
        file_path (path.Path): Path to the JSON file.
        key (str): If given, only this key of the JSON file will be returned.
            If the key does not exist, raise an `JsonContentInvalidError`
            error.

    Returns:
        dict: Content of the JSON file.

    Raises:
        JsonFileNotFoundError: If the JSON file cannot be found.
        JsonFileInvalidError: If the content of the JSON file cannot be parsed.
        JsonContentInvalidError: If the requested `key` cannot be found in the
            content of the JSON file.
    """
    try:
        content = json.loads(file_path.read_text())

    except FileNotFoundError as error:
        raise JsonFileNotFoundError(
            "Unable to find JSON file '{}'".format(file_path)
        ) from error

    except json.JSONDecodeError as error:
        raise JsonFileInvalidError(
            "Unable to parse JSON file '{}': {}".format(file_path, error)
        ) from error

    if key is None:
        return content

    try:
        return content[key]

    except KeyError as error:
        raise JsonContentInvalidError(
            "Unable to find key '{}' in JSON file '{}'".format(key, file_path)
        ) from error


class JsonFileNotFoundError(DakaraError, FileNotFoundError):
    """Exception raised if the JSON file does not exist."""


class JsonFileInvalidError(DakaraError):
    """Exception raised if the JSON file is invalid."""


class JsonContentInvalidError(DakaraError):
    """Exception raised if the content of the JSON file is unexpected."""
