"""Feeder for tags."""

import logging

from dakara_base.exceptions import DakaraError
from dakara_base.progress_bar import null_bar, progress_bar

from dakara_feeder.utils import clean_dict
from dakara_feeder.version import check_version
from dakara_feeder.web_client import HTTPClientDakara, TagAlreadyExistsError
from dakara_feeder.yaml import get_yaml_file_content

logger = logging.getLogger(__name__)


class TagsFeeder:
    """Class to feed the Dakara server database with tags.

    Args:
        config (dict): Dictionary of config.
        tags_file_path (path.Path): Path to the tags file.
        progress (bool): If `True`, a progress bar is displayed during long tasks.

    Attributes:
        bar (function): Progress bar to use.
        http_client (web_client.HTTPClientDakara): Client for the Dakara server.
        tags_file_path (str): Path to the tags file.
    """

    def __init__(self, config, tags_file_path, progress=True):
        # create objects
        self.http_client = HTTPClientDakara(config["server"], endpoint_prefix="api")
        self.tags_file_path = tags_file_path
        self.bar = progress_bar if progress else null_bar

    def load(self):
        """Execute side-effect initialization tasks."""
        # check version
        check_version()

        # authenticate to server
        self.http_client.load()
        self.http_client.authenticate()

    def feed(self):
        """Execute the feeding action.

        Raises:
            TagInvalidError: If the tag has either no name, or no color hue.
        """
        # load file and get the key
        tags = get_yaml_file_content(self.tags_file_path, "tags")
        logger.info("Found %i tags to create", len(tags))

        for index, tag in enumerate(self.bar(tags, text="Tags to create")):
            # check expected fields are present
            if "name" not in tag:
                raise TagInvalidError("Tag #{} must have a name".format(index))

            if "color_hue" not in tag:
                raise TagInvalidError("Tag #{} must have a color hue".format(index))

            # create corret tag (remove unnecessary keys)
            tag_correct = clean_dict(tag, ["name", "color_hue"])

            # try to create tag on server
            try:
                self.http_client.post_tag(tag_correct)

            except TagAlreadyExistsError:
                logger.info(
                    "Tag %s already exists on server and will not be updated",
                    tag["name"],
                )


class TagInvalidError(DakaraError):
    """Exception raised if a tag is invalid."""
