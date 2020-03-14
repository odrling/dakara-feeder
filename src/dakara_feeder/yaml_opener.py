import yaml

from dakara_base.exceptions import DakaraError


def get_yaml_file_content(file_path, key=None):
    """Load content of the given YAML file

    Arguments:
        file_path (path.Path): path to the YAML file.
        key (str): if given, only this key of the YAML file will be given. If
            the key does not exist, raise an YamlContentInvalidError error.

    Returns:
        dict: content of the tags file.

    Raises:
        YamlFileNotFoundError: if the YAML file cannot be found.
        YamlFileInvalidError: if the content of the YAML file cannot be parsed.
        YamlContentInvalidError: if the requested `key` cannot be found in the
            content of the YAML file.
    """
    try:
        content = yaml.load(file_path.text(), Loader=yaml.Loader)

    except FileNotFoundError as error:
        raise YamlFileNotFoundError(
            'Unable to find YAML file "{}"'.format(file_path)
        ) from error

    except yaml.YAMLError as error:
        raise YamlFileInvalidError(
            'Unable to parse YAML file "{}": {}'.format(file_path, error)
        ) from error

    if key is None:
        return content

    try:
        return content[key]

    except KeyError as error:
        raise YamlContentInvalidError(
            'Unable to find key "{}" in YAML file "{}"'.format(key, file_path)
        ) from error


class YamlFileNotFoundError(DakaraError, FileNotFoundError):
    """Exception raised if the YAML file does not exist
    """


class YamlFileInvalidError(DakaraError):
    """Exception raised if the YAML file is invalid
    """


class YamlContentInvalidError(DakaraError):
    """Exception raised if the content of the YAML file is unexpected
    """
