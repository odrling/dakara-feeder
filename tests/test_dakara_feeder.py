from datetime import timedelta
from unittest import TestCase
from unittest.mock import patch

from dakara_base.resources_manager import get_file
from path import Path

from dakara_feeder.dakara_feeder import DakaraFeeder
from dakara_feeder.directory_lister import SongPaths
from dakara_feeder.metadata_parser import FFProbeMetadataParser
from dakara_feeder.song import BaseSong
from dakara_feeder.subtitle_parser import Pysubs2SubtitleParser


class DakaraFeederTestCase(TestCase):
    """Test the feeder class
    """

    def test_check_version_release(self):
        """Test to display the version for a release
        """
        with self.assertLogs("dakara_feeder.dakara_feeder", "DEBUG") as logger:
            with patch.multiple(
                "dakara_feeder.dakara_feeder",
                __version__="0.0.0",
                __date__="1970-01-01",
            ):
                DakaraFeeder.check_version()

        # assert effect on logs
        self.assertListEqual(
            logger.output,
            ["INFO:dakara_feeder.dakara_feeder:" "Dakara feeder 0.0.0 (1970-01-01)"],
        )

    def test_check_version_non_release(self):
        """Test to display the version for a non release
        """
        with self.assertLogs("dakara_feeder.dakara_feeder", "DEBUG") as logger:
            with patch.multiple(
                "dakara_feeder.dakara_feeder",
                __version__="0.1.0-dev",
                __date__="1970-01-01",
            ):
                DakaraFeeder.check_version()

        # assert effect on logs
        self.assertListEqual(
            logger.output,
            [
                "INFO:dakara_feeder.dakara_feeder:"
                "Dakara feeder 0.1.0-dev (1970-01-01)",
                "WARNING:dakara_feeder.dakara_feeder:"
                "You are running a dev version, use it at your own risks!",
            ],
        )

    @patch("dakara_feeder.dakara_feeder.DakaraServer", autoset=True)
    @patch("dakara_feeder.dakara_feeder.get_custom_song", autoset=True)
    @patch.object(DakaraFeeder, "check_version", autoset=True)
    def test_load_no_song_class(
        self, mocked_check_version, mocked_get_custom_song, mocked_dakara_server_class
    ):
        """Test to run side-effect tasks
        """
        # create the config
        config = {"server": {}, "kara_folder": "basepath"}

        # create the object
        feeder = DakaraFeeder(config, progress=False)

        # pre assert
        self.assertIs(feeder.song_class, BaseSong)

        # call the method
        feeder.load()

        # post assert
        self.assertIs(feeder.song_class, BaseSong)

        # assert the call
        mocked_check_version.assert_called_with()
        mocked_get_custom_song.assert_not_called()
        mocked_dakara_server_class.return_value.authenticate.assert_called_with()

    @patch("dakara_feeder.dakara_feeder.DakaraServer", autoset=True)
    @patch("dakara_feeder.dakara_feeder.get_custom_song", autoset=True)
    @patch.object(DakaraFeeder, "check_version", autoset=True)
    def test_load_with_song_class(
        self, mocked_check_version, mocked_get_custom_song, mocked_dakara_server_class
    ):
        """Test to run side-effect tasks
        """

        class MySong(BaseSong):
            pass

        # prepare mocks
        mocked_get_custom_song.return_value = MySong
        # create the config
        config = {
            "server": {},
            "kara_folder": "basepath",
            "custom_song_class": "module.MySong",
        }

        # create the object
        feeder = DakaraFeeder(config, progress=False)

        # pre assert
        self.assertIs(feeder.song_class, BaseSong)

        # call the method
        feeder.load()

        # post assert
        self.assertIs(feeder.song_class, MySong)

        # assert the call
        mocked_get_custom_song.assert_called_with("module.MySong")

    @patch.object(Pysubs2SubtitleParser, "parse", autoset=True)
    @patch.object(FFProbeMetadataParser, "parse", autoset=True)
    @patch("dakara_feeder.dakara_feeder.list_directory", autoset=True)
    @patch("dakara_feeder.dakara_feeder.DakaraServer", autoset=True)
    def test_feed(
        self,
        mocked_dakara_server_class,
        mocked_list_directory,
        mocked_metadata_parse,
        mocked_subtitle_parse,
    ):
        """Test to feed
        """
        # create the mocks
        mocked_dakara_server_class.return_value.get_songs.return_value = [
            {"id": 0, "path": Path("directory_0/song_0.mp4").normpath()},
            {"id": 1, "path": Path("directory_1/music_1.mp4").normpath()},
        ]
        mocked_list_directory.return_value = [
            SongPaths(Path("directory_0/song_0.mp4").normpath()),
            SongPaths(
                Path("directory_2/song_2.mp4").normpath(),
                Path("directory_2/song_2.ass").normpath(),
            ),
        ]
        mocked_metadata_parse.return_value.get_duration.return_value = timedelta(
            seconds=1
        )
        mocked_subtitle_parse.return_value.get_lyrics.return_value = "lyri lyri"

        # create the config
        config = {"server": {}, "kara_folder": "basepath"}

        # create the object
        feeder = DakaraFeeder(config, progress=False)

        # call the method
        with self.assertLogs("dakara_feeder.dakara_feeder", "DEBUG") as logger_feeder:
            with self.assertLogs("dakara_base.progress_bar") as logger_progress:
                feeder.feed()

        # assert the mocked calls
        mocked_dakara_server_class.return_value.get_songs.assert_called_with()
        mocked_list_directory.assert_called_with("basepath")
        mocked_dakara_server_class.return_value.post_song.assert_called_with(
            [
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
                    "lyrics": "lyri lyri",
                }
            ]
        )
        mocked_dakara_server_class.return_value.delete_song.assert_called_with(1)
        mocked_subtitle_parse.assert_called_with(
            Path("basepath/directory_2/song_2.ass").normpath()
        )
        mocked_subtitle_parse.return_value.get_lyrics.assert_called_with()

        self.assertListEqual(
            logger_feeder.output,
            [
                "INFO:dakara_feeder.dakara_feeder:Found 2 songs in server",
                "INFO:dakara_feeder.dakara_feeder:Found 2 songs in local directory",
                "INFO:dakara_feeder.dakara_feeder:Found 1 songs to add",
                "INFO:dakara_feeder.dakara_feeder:Found 1 songs to delete",
                "INFO:dakara_feeder.dakara_feeder:Found 0 songs to update",
            ],
        )
        self.assertListEqual(
            logger_progress.output,
            [
                "INFO:dakara_base.progress_bar:Parsing songs to add",
                "INFO:dakara_base.progress_bar:Uploading added songs",
                "INFO:dakara_base.progress_bar:Deleting removed songs",
            ],
        )

    @patch.object(FFProbeMetadataParser, "parse", autoset=True)
    @patch("dakara_feeder.dakara_feeder.list_directory", autoset=True)
    @patch("dakara_feeder.dakara_feeder.DakaraServer", autoset=True)
    def test_renamed_file(
        self, mocked_dakara_server_class, mocked_list_directory, mocked_metadata_parse
    ):
        """Test feed when a file has been renamed
        """
        # mock content of server (old files)
        mocked_dakara_server_class.return_value.get_songs.return_value = [
            {"id": 0, "path": Path("directory_0/song.mp4").normpath()},
            {"id": 1, "path": Path("directory_1/music.mp4").normpath()},
        ]

        # mock content of file system (new files)
        # Simulate file music.mp4 renamed to musics.mp4
        mocked_list_directory.return_value = [
            SongPaths(Path("directory_0/song.mp4").normpath()),
            SongPaths(Path("directory_1/musics.mp4").normpath()),
        ]
        mocked_metadata_parse.return_value.get_duration.return_value = timedelta(
            seconds=1
        )

        # create the config
        config = {"server": {}, "kara_folder": "basepath"}

        # create the object
        feeder = DakaraFeeder(config, progress=False)

        # call the method
        with self.assertLogs("dakara_feeder.dakara_feeder", "DEBUG") as logger:
            with self.assertLogs("dakara_base.progress_bar"):
                feeder.feed()

        # assert the mocked calls
        mocked_dakara_server_class.return_value.get_songs.assert_called_with()
        mocked_list_directory.assert_called_with("basepath")
        mocked_dakara_server_class.return_value.put_song.assert_called_with(
            1,
            {
                "title": "musics",
                "filename": "musics.mp4",
                "directory": "directory_1",
                "duration": 1,
                "artists": [],
                "works": [],
                "tags": [],
                "version": "",
                "detail": "",
                "detail_video": "",
                "lyrics": "",
            },
        )
        self.assertListEqual(
            logger.output,
            [
                "INFO:dakara_feeder.dakara_feeder:Found 2 songs in server",
                "INFO:dakara_feeder.dakara_feeder:Found 2 songs in local directory",
                "INFO:dakara_feeder.dakara_feeder:Found 0 songs to add",
                "INFO:dakara_feeder.dakara_feeder:Found 0 songs to delete",
                "INFO:dakara_feeder.dakara_feeder:Found 1 songs to update",
            ],
        )

    @patch.object(Pysubs2SubtitleParser, "parse", autoset=True)
    @patch.object(FFProbeMetadataParser, "parse", autoset=True)
    @patch("dakara_feeder.dakara_feeder.list_directory", autoset=True)
    @patch("dakara_feeder.dakara_feeder.DakaraServer", autoset=True)
    def test_feed_with_force_update(
        self,
        mocked_dakara_server_class,
        mocked_list_directory,
        mocked_metadata_parse,
        mocked_subtitle_parse,
    ):
        """Test to feed
        """
        # create the mocks
        mocked_dakara_server_class.return_value.get_songs.return_value = [
            {"id": 1, "path": Path("music_1.mp4")}
        ]
        mocked_list_directory.return_value = [
            SongPaths(Path("music_1.mp4"), Path("music_1.ass"))
        ]
        mocked_metadata_parse.return_value.get_duration.return_value = timedelta(
            seconds=1
        )
        mocked_subtitle_parse.return_value.get_lyrics.return_value = "lyri lyri"

        # create the config
        config = {"server": {}, "kara_folder": "basepath"}

        # create the object
        feeder = DakaraFeeder(config, force_update=True, progress=False)

        # call the method
        with self.assertLogs("dakara_feeder.dakara_feeder", "DEBUG") as logger:
            with self.assertLogs("dakara_base.progress_bar"):
                feeder.feed()

        # assert the mocked calls
        mocked_dakara_server_class.return_value.get_songs.assert_called_with()
        mocked_list_directory.assert_called_with("basepath")
        mocked_dakara_server_class.return_value.put_song.assert_called_with(
            1,
            {
                "title": "music_1",
                "filename": "music_1.mp4",
                "directory": "",
                "duration": 1,
                "artists": [],
                "works": [],
                "tags": [],
                "version": "",
                "detail": "",
                "detail_video": "",
                "lyrics": "lyri lyri",
            },
        )

        self.assertListEqual(
            logger.output,
            [
                "INFO:dakara_feeder.dakara_feeder:Found 1 songs in server",
                "INFO:dakara_feeder.dakara_feeder:Found 1 songs in local directory",
                "INFO:dakara_feeder.dakara_feeder:Found 0 songs to add",
                "INFO:dakara_feeder.dakara_feeder:Found 0 songs to delete",
                "INFO:dakara_feeder.dakara_feeder:Found 1 songs to update",
            ],
        )

    @patch.object(Pysubs2SubtitleParser, "parse", autoset=True)
    @patch.object(FFProbeMetadataParser, "parse", autoset=True)
    @patch("dakara_feeder.dakara_feeder.list_directory", autoset=True)
    @patch("dakara_feeder.dakara_feeder.DakaraServer", autoset=True)
    def test_create_two_songs(
        self,
        mocked_dakara_server_class,
        mocked_list_directory,
        mocked_metadata_parse,
        mocked_subtitle_parse,
    ):
        """Test to create two songs
        """
        # create the mocks
        mocked_dakara_server_class.return_value.get_songs.return_value = []
        mocked_list_directory.return_value = [
            SongPaths(Path("directory_0/song_0.mp4").normpath()),
            SongPaths(Path("directory_1/song_1.mp4").normpath()),
        ]
        mocked_metadata_parse.return_value.get_duration.return_value = timedelta(
            seconds=1
        )

        # create the config
        config = {"server": {}, "kara_folder": "basepath"}

        # create the object
        feeder = DakaraFeeder(config, progress=False)

        # call the method
        with self.assertLogs("dakara_feeder.dakara_feeder", "DEBUG") as logger:
            with self.assertLogs("dakara_base.progress_bar"):
                feeder.feed()

        # assert the mocked calls
        mocked_dakara_server_class.return_value.get_songs.assert_called_with()
        mocked_list_directory.assert_called_with("basepath")
        songs = [
            {
                "title": "song_0",
                "filename": "song_0.mp4",
                "directory": "directory_0",
                "duration": 1,
                "artists": [],
                "works": [],
                "tags": [],
                "version": "",
                "detail": "",
                "detail_video": "",
                "lyrics": "",
            },
            {
                "title": "song_1",
                "filename": "song_1.mp4",
                "directory": "directory_1",
                "duration": 1,
                "artists": [],
                "works": [],
                "tags": [],
                "version": "",
                "detail": "",
                "detail_video": "",
                "lyrics": "",
            },
        ]
        post_calls = mocked_dakara_server_class.return_value.post_song.mock_calls

        # check called once
        self.assertEqual(len(post_calls), 1)

        # check one positional argument
        _, args, kwargs, = post_calls[0]
        self.assertEqual(len(args), 1)
        self.assertEqual(len(kwargs), 0)

        # check first arguement is the list of the two expected songs
        self.assertCountEqual(args[0], songs)
        mocked_dakara_server_class.return_value.delete_song.assert_not_called()

        self.assertListEqual(
            logger.output,
            [
                "INFO:dakara_feeder.dakara_feeder:Found 0 songs in server",
                "INFO:dakara_feeder.dakara_feeder:Found 2 songs in local directory",
                "INFO:dakara_feeder.dakara_feeder:Found 2 songs to add",
                "INFO:dakara_feeder.dakara_feeder:Found 0 songs to delete",
                "INFO:dakara_feeder.dakara_feeder:Found 0 songs to update",
            ],
        )

    @patch.object(FFProbeMetadataParser, "parse", autoset=True)
    @patch("dakara_feeder.dakara_feeder.list_directory", autoset=True)
    @patch("dakara_feeder.dakara_feeder.DakaraServer", autoset=True)
    def test_feed_custom_song_class(
        self, mocked_dakara_server_class, mocked_list_directory, mocked_metadata_parse
    ):
        """Test to feed using a custom song class
        """
        # create the mocks
        mocked_dakara_server_class.return_value.get_songs.return_value = []
        mocked_list_directory.return_value = [
            SongPaths(Path("directory_0/song_0.mp4").normpath())
        ]
        mocked_metadata_parse.return_value.get_duration.return_value = timedelta(
            seconds=1
        )

        class Song(BaseSong):
            def get_artists(self):
                return ["artist1", "artist2"]

        # create the config
        config = {
            "server": {},
            "custom_song_class": "custom_song_module",
            "kara_folder": "basepath",
        }

        # create the object
        feeder = DakaraFeeder(config, progress=False)
        feeder.song_class = Song

        # call the method
        with self.assertLogs("dakara_feeder.dakara_feeder", "DEBUG"):
            with self.assertLogs("dakara_base.progress_bar"):
                feeder.feed()

        # assert the mocked calls
        mocked_dakara_server_class.return_value.post_song.assert_called_with(
            [
                {
                    "title": "song_0",
                    "filename": "song_0.mp4",
                    "directory": "directory_0",
                    "duration": 1,
                    "artists": ["artist1", "artist2"],
                    "works": [],
                    "tags": [],
                    "version": "",
                    "detail": "",
                    "detail_video": "",
                    "lyrics": "",
                }
            ]
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
        config = {"server": {}, "kara_folder": get_file("tests.resources", "")}
        feeder = DakaraFeeder(config, progress=False)

        # call the method
        with self.assertLogs("dakara_feeder.dakara_feeder", "DEBUG"):
            with self.assertLogs("dakara_base.progress_bar"):
                feeder.feed()

        # assert the mocked calls
        mocked_dakara_server_class.return_value.get_songs.assert_called_with()
        mocked_dakara_server_class.return_value.post_song.assert_called_with(
            [
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
                    "lyrics": "Piyo!",
                }
            ]
        )
