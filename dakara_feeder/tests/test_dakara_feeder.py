from unittest import TestCase
from unittest.mock import patch, MagicMock, ANY

from path import Path

from dakara_feeder.dakara_feeder import DakaraFeeder


class DakaraFeederTestCase(TestCase):
    """Test the `Feeder` class
    """

    @patch("dakara_feeder.dakara_feeder.list_directory")
    @patch("dakara_feeder.dakara_feeder.DakaraServer")
    @patch.object(DakaraFeeder, "load_config")
    def test_feed(
        self, mocked_load_config, mocked_dakara_server_class, mocked_list_directory
    ):
        """Test to feed
        """
        # create the mocks
        mocked_dakara_server_class.return_value.get_songs.return_value = [
            Path("directory_0/song_0.mp4"),
            Path("directory_1/song_1.mp4"),
        ]
        mocked_list_directory.return_value = [
            Path("directory_0/song_0.mp4"),
            Path("directory_2/song_2.mp4"),
        ]

        # create the object
        feeder = DakaraFeeder(MagicMock(), MagicMock())

        # call the method
        with self.assertLogs("dakara_feeder.dakara_feeder", "DEBUG") as logger:
            feeder.feed()

        # assert the mocked calls
        mocked_dakara_server_class.return_value.get_songs.assert_called_with()
        mocked_list_directory.assert_called_with(ANY)
        mocked_dakara_server_class.return_value.post_songs_diff.assert_called_with(
            [
                {
                    "title": "song_2",
                    "filename": "song_2.mp4",
                    "directory": "directory_2",
                    "duration": 0,
                }
            ],
            [{"filename": "song_1.mp4", "directory": "directory_1"}],
        )

        self.assertListEqual(
            logger.output,
            [
                "DEBUG:dakara_feeder.dakara_feeder:Found 2 songs in server",
                "DEBUG:dakara_feeder.dakara_feeder:Found 2 songs in local directory",
                "DEBUG:dakara_feeder.dakara_feeder:Found 1 songs to add",
                "DEBUG:dakara_feeder.dakara_feeder:Found 1 songs to delete",
            ],
        )
