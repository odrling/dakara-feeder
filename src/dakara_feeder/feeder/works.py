"""Feeder for works."""

import logging

from dakara_base.exceptions import DakaraError
from dakara_base.progress_bar import null_bar, progress_bar

from dakara_feeder.difference import generate_diff
from dakara_feeder.json import get_json_file_content
from dakara_feeder.utils import divide_chunks
from dakara_feeder.version import check_version
from dakara_feeder.web_client import HTTPClientDakara

logger = logging.getLogger(__name__)


WORKS_PER_CHUNK = 100


class WorksFeeder:
    """Class to feed the Dakara server database with works.

    Args:
        config (dict): Dictionary of config.
        works_file_path (path.Path): Path to the JSON file containing works.
        update_only (bool): If `True`, will not create works that do not exist on
            the server.
        progress (bool): If `True`, a progress bar is displayed during long tasks.

    Attributes:
        http_client (web_client.HTTPClientDakara): Client for the Dakara server.
        bar (function): Progress bar to use.
        works_file_path (path.Path): Path to the JSON file containing works.
        update_only (bool): If `True`, will not create works that do not exist on
            the server.
    """

    def __init__(self, config, works_file_path, update_only=False, progress=True):
        # create objects
        self.http_client = HTTPClientDakara(config["server"], endpoint_prefix="api")
        self.bar = progress_bar if progress else null_bar
        self.works_file_path = works_file_path
        self.update_only = update_only
        self.works_per_chunk = config["server"].get("works_per_chunk", WORKS_PER_CHUNK)

    def load(self):
        """Execute side-effect initialization tasks."""
        # check version
        check_version()

        # authenticate to server
        self.http_client.load()
        self.http_client.authenticate()

    @staticmethod
    def stringify_work(work):
        """Create a string version of a work.

        The string contains the title, the subtitle (replaced by an empty string
        if not present) and the query name of the work type. The string is made
        lower case.

        Args:
            work (dict): Work to stringiny, with the same structure accepted by
                the server.

        Returns:
            str: Stringified version of the work.
        """
        return "-".join(
            [work["title"], work.get("subtitle", ""), work["work_type"]["query_name"]]
        ).lower()

    def check(self, works_by_type):
        """Check works format.

        Args:
            works_by_type (dict): Key is work type, value is list of
                representation of works.

        Raises:
            WorksInvalidError: If works of a work type are not stored in a
                list.
            WorkInvalidError: If one work has no title.
        """
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

            # check work has a title
            for index_work, work in enumerate(works):
                if "title" not in work:
                    raise WorkInvalidError(
                        "Work of type {} #{} must have a title".format(
                            work_type_query_name, index_work
                        )
                    )

                if "alternavite_titles" in work:
                    # check the alternative title is set with a dict
                    for index_alternative_title, alternative_title in enumerate(
                        work["alternavite_titles"]
                    ):
                        if "title" not in alternative_title:
                            raise WorkInvalidError(
                                "Alternative title #{} of work of type {} #{} "
                                "must be set with the key 'title'".format(
                                    index_alternative_title,
                                    work_type_query_name,
                                    index_work,
                                )
                            )

    def feed(self):
        """Execute the feeding action."""
        # get list of works on the server
        old_works = self.http_client.retrieve_works()
        logger.info("Found %i works in server", len(old_works))

        old_works_by_str = {self.stringify_work(w): w for w in old_works}
        old_works_str = list(old_works_by_str.keys())

        # get list of works on file
        works_by_type = get_json_file_content(self.works_file_path)
        logger.info(
            "Found %i work types and %i works to create",
            len(works_by_type),
            sum(len(ws) for ws in works_by_type.values()),
        )

        # check works validity
        self.check(works_by_type)

        # reformat works to include the work type
        new_works = [
            {**w, "work_type": {"query_name": qn}}
            for qn, ws in works_by_type.items()
            for w in ws
        ]
        new_works_by_str = {self.stringify_work(w): w for w in new_works}
        new_works_str = list(new_works_by_str.keys())

        # separate works to add and works to update
        added_works_str, _, updated_works_str = generate_diff(
            old_works_str, new_works_str
        )

        if not self.update_only:
            logger.info("Found %i works to add", len(added_works_str))

        logger.info("Found %i works to update", len(updated_works_str))

        # works to add
        if not self.update_only and added_works_str:
            # upload to server by chunks
            for work_str_chunk in self.bar(
                list(divide_chunks(added_works_str, self.works_per_chunk)),
                text="Uploading added works",
            ):
                self.http_client.post_work(
                    [new_works_by_str[ws] for ws in work_str_chunk]
                )

        # works to update
        if updated_works_str:
            # upload to server
            for work_str in self.bar(updated_works_str, text="Uploading updated works"):
                work = new_works_by_str[work_str]
                id = old_works_by_str[work_str]["id"]
                self.http_client.put_work(id, work)


class WorksInvalidError(DakaraError):
    """Exception raised if a list of works is invalid."""


class WorkInvalidError(DakaraError):
    """Exception raised if a work is invalid."""
