import logging

from path import Path

from dakara_base.exceptions import DakaraError
from dakara_base.progress_bar import progress_bar, null_bar
from dakara_feeder.dakara_server import DakaraServer, TagAlreadyExistsError
from dakara_feeder.utils import clean_dict
from dakara_feeder.version import check_version
from dakara_feeder.yaml_opener import get_yaml_file_content


logger = logging.getLogger(__name__)


class TagsFeeder:
    """Class for the Dakara tags feeder

    Args:
        config (dict): dictionary of config.
        tags_file_path (str): path to the tags file.
        progress (bool): if True, a progress bar is displayed during long tasks.

    Attributes:
        bar (function): progress bar to use.
        dakara_server (dakara_server.DakaraServer): client for the Dakara server.
        tags_file_path (str): path to the tags file.
    """

    def __init__(self, config, tags_file_path, progress=True):
        # create objects
        self.dakara_server = DakaraServer(config["server"], endpoint_prefix="api")
        self.tags_file_path = Path(tags_file_path)
        self.bar = progress_bar if progress else null_bar

    def load(self):
        """Execute side-effect initialization tasks
        """
        # check version
        check_version()

        # authenticate to server
        self.dakara_server.authenticate()

    def feed(self):
        """Execute the feeding action
        """
        # load file and get the key
        tags = get_yaml_file_content(self.tags_file_path, "tags")

        for index, tag in enumerate(self.bar(tags, text="Tags to create")):
            # check expected fields are present
            if "name" not in tag:
                raise InvalidTag("Tag {} must have a name".format(index))

            if "color_hue" not in tag:
                raise InvalidTag("Tag {} must have a color hue".format(index))

            # create corret tag (remove unnecessary keys)
            tag_correct = clean_dict(tag, ["name", "color_hue"])

            # try to create tag on server
            try:
                self.dakara_server.create_tag(tag_correct)

            except TagAlreadyExistsError:
                logger.info(
                    "Tag %s already exists on server and will not be updated",
                    tag["name"],
                )


class InvalidTag(DakaraError):
    """Exception raised if a tag is invalid
    """
