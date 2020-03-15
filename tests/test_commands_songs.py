from argparse import Namespace
from unittest import TestCase
from unittest.mock import ANY, patch

from path import Path

from dakara_feeder import SongsFeeder
from dakara_feeder.commands.songs import SongsSubcommand


class SongsTestCase(TestCase):
    """Test the songs subcommand
    """

    @patch.object(SongsFeeder, "feed")
    @patch.object(SongsSubcommand, "load_feeder")
    @patch.object(SongsSubcommand, "load_config")
    def test_feed(
        self, mocked_load_config, mocked_load_feeder, mocked_feed,
    ):
        """Test to feed songs
        """
        subcommand = SongsSubcommand()

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
            Namespace(debug=False, force=False, progress=True, prune=True)
        )

        # assert the call
        mocked_load_config.assert_called_with(False)
        mocked_load_feeder.assert_called_with(ANY)
        mocked_feed.assert_called_with()
