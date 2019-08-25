from unittest import TestCase
from unittest.mock import patch, MagicMock, ANY
from datetime import timedelta

from dakara_base.resources_manager import get_file
from path import Path

from dakara_feeder.dakara_feeder import DakaraFeeder
from dakara_feeder.directory_lister import SongPaths
from dakara_feeder.metadata_parser import FFProbeMetadataParser


class DakaraFeederTestCase(TestCase):
    """Test the feeder class
    """

    @patch.object(FFProbeMetadataParser, "parse", autoset=True)
    @patch("dakara_feeder.dakara_feeder.list_directory", autoset=True)
    @patch("dakara_feeder.dakara_feeder.DakaraServer", autoset=True)
    def test_feed(
        self, mocked_dakara_server_class, mocked_list_directory, mocked_parse
    ):
        """Test to feed
        """
        # create the mocks
        mocked_dakara_server_class.return_value.get_songs.return_value = [
            {"id": 0, "path": Path("directory_0/song_0.mp4")},
            {"id": 1, "path": Path("directory_1/song_1.mp4")},
        ]
        mocked_list_directory.return_value = [
            SongPaths(Path("directory_0/song_0.mp4")),
            SongPaths(Path("directory_2/song_2.mp4")),
        ]
        mocked_parse.return_value.duration = timedelta(seconds=1)

        # create the object
        feeder = DakaraFeeder(MagicMock())

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


class DakaraFeederIntegrationTestCase(TestCase):
    """Integration test for the Feeder class
    """

    @patch("dakara_feeder.dakara_feeder.DakaraServer", autoset=True)
    def test_feed(self, mocked_dakara_server_class):
        """Test to feed
        """
        # create the mocks
        mocked_dakara_server_class.return_value.get_songs.return_value = []

        # create the object
        config = {
            "server": {},
            "kara_folder": get_file("dakara_feeder.tests.resources", ""),
        }
        feeder = DakaraFeeder(config)

        # call the method
        with self.assertLogs("dakara_feeder.dakara_feeder", "DEBUG"):
            feeder.feed()

        # assert the mocked calls
        mocked_dakara_server_class.return_value.get_songs.assert_called_with()
        mocked_dakara_server_class.return_value.post_song.assert_called_with(
            {
                "title": "dummy",
                "filename": "dummy.mkv",
                "directory": "",
                "duration": 2,
                "artists": [],
                "works": [],
                "tags": [],
                "version": "",
                "detail": "",
                "detail_video": "",
                "lyrics": "",
            }
        )
