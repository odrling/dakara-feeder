from unittest import TestCase
from unittest.mock import patch, MagicMock, ANY
from datetime import timedelta

from path import Path

from dakara_feeder.dakara_feeder import DakaraFeeder
from dakara_feeder.metadata_parser import FFProbeMetadataParser


class DakaraFeederTestCase(TestCase):
    """Test the `Feeder` class
    """

    @patch.object(FFProbeMetadataParser, "parse")
    @patch("dakara_feeder.dakara_feeder.list_directory")
    @patch("dakara_feeder.dakara_feeder.DakaraServer")
    @patch.object(DakaraFeeder, "load_config")
    def test_feed(
        self,
        mocked_load_config,
        mocked_dakara_server_class,
        mocked_list_directory,
        mocked_parse,
    ):
        """Test to feed
        """
        # create the mocks
        mocked_dakara_server_class.return_value.get_songs.return_value = [
            {"id": 0, "path": Path("directory_0/song_0.mp4")},
            {"id": 1, "path": Path("directory_1/song_1.mp4")},
        ]
        mocked_list_directory.return_value = [
            Path("directory_0/song_0.mp4"),
            Path("directory_2/song_2.mp4"),
        ]
        mocked_parse.return_value.duration = timedelta(seconds=1)

        # create the object
        feeder = DakaraFeeder(MagicMock(), MagicMock())

        # call the method
        with self.assertLogs("dakara_feeder.dakara_feeder", "DEBUG") as logger:
            feeder.feed()

        # assert the mocked calls
        mocked_dakara_server_class.return_value.get_songs.assert_called_with()
        mocked_list_directory.assert_called_with(ANY)
        mocked_dakara_server_class.return_value.post_song.assert_called_with(
            {
                "title": "song_2",
                "filename": "song_2.mp4",
                "directory": "directory_2",
                "duration": 1,
                "artists": [],
                "works": [],
                "tags": [],
                "version": "",
                "detail": "",
                "detail_video": "",
                "lyrics": "",
            }
        )
        mocked_dakara_server_class.return_value.delete_song.assert_called_with(1)

        self.assertListEqual(
            logger.output,
            [
                "DEBUG:dakara_feeder.dakara_feeder:Found 2 songs in server",
                "DEBUG:dakara_feeder.dakara_feeder:Found 2 songs in local directory",
                "DEBUG:dakara_feeder.dakara_feeder:Found 1 songs to add",
                "DEBUG:dakara_feeder.dakara_feeder:Found 1 songs to delete",
            ],
        )
