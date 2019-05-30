from unittest import TestCase
from unittest.mock import patch, MagicMock, ANY

from dakara_feeder.feeder import Feeder


class FeederTestCase(TestCase):
    """Test the `Feeder` class
    """

    @patch("dakara_feeder.feeder.list_directory")
    @patch("dakara_feeder.feeder.DakaraServer")
    @patch.object(Feeder, "load_config")
    def test_feed(self, mocked_load_config, mocked_dakara_server_class, mocked_list_directory):
        """Test to feed
        """
        # create the mocks
        mocked_dakara_server_class.return_value.get_songs.return_value = [
            "directory_0/song_0.mp4",
            "directory_1/song_1.mp4",
        ]
        mocked_list_directory.return_value = [
            "directory_0/song_0.mp4",
            "directory_2/song_2.mp4",
        ]

        # create the object
        feeder = Feeder(MagicMock(), MagicMock())

        # call the method
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
                }
            ],
            [
                {
                    "filename": "song_1.mp4",
                    "directory": "directory_1",
                }
            ]
        )

