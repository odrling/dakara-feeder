from argparse import Namespace
from unittest import TestCase
from unittest.mock import ANY, patch

from path import Path

from dakara_feeder import WorkTypesFeeder
from dakara_feeder.commands.work_types import WorkTypesSubcommand


class WorkTypesTestCase(TestCase):
    """Test the work types subcommand"""

    @patch.object(WorkTypesFeeder, "feed")
    @patch.object(WorkTypesSubcommand, "load_feeder")
    @patch.object(WorkTypesSubcommand, "load_config")
    def test_feed(
        self,
        mocked_load_config,
        mocked_load_feeder,
        mocked_feed,
    ):
        """Test to feed work types"""
        subcommand = WorkTypesSubcommand()

        # setup the mocks
        config = {
            "kara_folder": Path("path") / "to" / "folder",
            "server": {
                "url": "www.example.com",
                "login": "login",
                "password": "password",
            },
        }
        mocked_load_config.return_value = config

        # call the function
        subcommand.handle(
            Namespace(
                debug=False,
                file=Path("path") / "to" / "work_types" / "file",
                progress=True,
            )
        )

        # assert the call
        mocked_load_config.assert_called_with(False)
        mocked_load_feeder.assert_called_with(ANY)
        mocked_feed.assert_called_with()
