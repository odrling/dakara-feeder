from argparse import Namespace
from unittest import TestCase
from unittest.mock import ANY, patch

from path import Path

from dakara_feeder import TagsFeeder
from dakara_feeder.commands.tags import TagsSubcommand


class TagsTestCase(TestCase):
    """Test the tags subcommand
    """

    @patch.object(TagsFeeder, "feed")
    @patch.object(TagsSubcommand, "load_feeder")
    @patch.object(TagsSubcommand, "load_config")
    def test_feed(
        self, mocked_load_config, mocked_load_feeder, mocked_feed,
    ):
        """Test to feed tags
        """
        subcommand = TagsSubcommand()

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
                debug=False, file=Path("path") / "to" / "tags" / "file", progress=True
            )
        )

        # assert the call
        mocked_load_config.assert_called_with(False)
        mocked_load_feeder.assert_called_with(ANY)
        mocked_feed.assert_called_with()
