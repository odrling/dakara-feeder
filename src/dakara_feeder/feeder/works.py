"""Feeder for works."""

import logging

from dakara_base.exceptions import DakaraError
from dakara_base.progress_bar import null_bar, progress_bar

from dakara_feeder.web_client import HTTPClientDakara
from dakara_feeder.yaml import get_yaml_file_content
from dakara_feeder.version import check_version


class WorkFeeder:
    def __init__(self, config, works_file_path, update_only=False, progress=True):
        # create objects
        self.http_client = HTTPClientDakara(config["server"], endpoint_prefix="api")
        self.bar = progress_bar if progress else null_bar
        self.works_file_path = works_file_path
        self.update_only = update_only

    def load(self):
        """Execute side-effect initialization tasks."""
        # check version
        check_version()

        # authenticate to server
        self.http_client.authenticate()

    def feed(self):
        # load file
        works_by_type = get_yaml_file_content(self.works_file_path, "works")
        logger.info(
            "Found %i work types and %i works to create",
            len(works_by_type),
            sum(len(ws) for ws in works_by_type.values()),
        )

        for work_type_query_name, works in self.bar(
            works_by_type.items(), text="Checking works"
        ):
            # check works is a list
            if not isinstance(works, list):
                raise WorksInvalidError(
                    "Works of type {} must be stored in a list".format(
                        work_type_query_name
                    )
                )

            for index, work in enumerate(works):
                if "title" not in work:
                    raise WorkInvalidError(
                        "Work {} #{} must have a title".format(
                            work_type_query_name, index
                        )
                    )


class WorksInvalidError(DakaraError):
    """Exception raised if a list of works is invalid."""


class WorkInvalidError(DakaraError):
    """Exception raised if a work is invalid."""
