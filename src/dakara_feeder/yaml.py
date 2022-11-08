"""Open YAML files safely."""

import yaml
from dakara_base.exceptions import DakaraError


def get_yaml_file_content(file_path, key=None):
    """Load content of the given YAML file.

    Args:
        file_path (path.Path): Path to the YAML file.
        key (str): If given, only this key of the YAML file will be given. If
            the key does not exist, raise an YamlContentInvalidError error.

    Returns:
        dict: Content of the YAML file.

    Raises:
        YamlFileNotFoundError: If the YAML file cannot be found.
        YamlFileInvalidError: If the content of the YAML file cannot be parsed.
        YamlContentInvalidError: If the requested `key` cannot be found in the
            content of the YAML file.
    """
    try:
        content = yaml.safe_load(file_path.read_text())

    except FileNotFoundError as error:
        raise YamlFileNotFoundError(
            "Unable to find YAML file '{}'".format(file_path)
        ) from error

    except yaml.YAMLError as error:
        raise YamlFileInvalidError(
            "Unable to parse YAML file '{}': {}".format(file_path, error)
        ) from error

    if key is None:
        return content

    try:
        return content[key]

    except KeyError as error:
        raise YamlContentInvalidError(
            "Unable to find key '{}' in YAML file '{}'".format(key, file_path)
        ) from error


class YamlFileNotFoundError(DakaraError, FileNotFoundError):
    """Exception raised if the YAML file does not exist."""


class YamlFileInvalidError(DakaraError):
    """Exception raised if the YAML file is invalid."""


class YamlContentInvalidError(DakaraError):
    """Exception raised if the content of the YAML file is unexpected."""
