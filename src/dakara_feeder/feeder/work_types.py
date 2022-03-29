"""Feeder for work types."""

import logging

from dakara_base.exceptions import DakaraError
from dakara_base.progress_bar import null_bar, progress_bar

from dakara_feeder.utils import clean_dict
from dakara_feeder.version import check_version
from dakara_feeder.web_client import HTTPClientDakara, WorkTypeAlreadyExistsError
from dakara_feeder.yaml import get_yaml_file_content

logger = logging.getLogger(__name__)


class WorkTypesFeeder:
    """Class to feed the Dakara server database with work types.

    Args:
        config (dict): Dictionary of config.
        work_types_file_path (path.Path): Path to the work types file.
        progress (bool): If `True`, a progress bar is displayed during long tasks.

    Attributes:
        bar (function): Progress bar to use.
        http_client (web_client.HTTPClientDakara): Client for the Dakara server.
        work_types_file_path (str): Path to the work types file.
    """

    def __init__(self, config, work_types_file_path, progress=True):
        # create objects
        self.http_client = HTTPClientDakara(config["server"], endpoint_prefix="api")
        self.work_types_file_path = work_types_file_path
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
            WorkTypeInvalidError: If the work type has either no query name, no
                name or plural name.
        """
        # load file and get the key
        work_types = get_yaml_file_content(self.work_types_file_path, "worktypes")
        logger.info("Found %i work types to create", len(work_types))

        for index, work_type in enumerate(
            self.bar(work_types, text="WorkTypes to create")
        ):
            # check expected fields are present
            if "query_name" not in work_type:
                raise WorkTypeInvalidError(
                    "Work type #{} must have a query name".format(index)
                )

            if "name" not in work_type:
                raise WorkTypeInvalidError(
                    "Work type #{} must have a name".format(index)
                )

            if "name_plural" not in work_type:
                raise WorkTypeInvalidError(
                    "Work type #{} must have a plural name".format(index)
                )

            # create corret work type (remove unnecessary keys)
            work_type_correct = clean_dict(
                work_type, ["query_name", "name", "name_plural", "icon_name"]
            )

            # try to create work type on server
            try:
                self.http_client.post_work_type(work_type_correct)

            except WorkTypeAlreadyExistsError:
                logger.info(
                    "Work type %s already exists on server and will not be updated",
                    work_type["query_name"],
                )


class WorkTypeInvalidError(DakaraError):
    """Exception raised if a work type is invalid."""
