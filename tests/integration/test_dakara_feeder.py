from unittest import TestCase, skipUnless
from unittest.mock import patch

try:
    from importlib.resources import path

except ImportError:
    from importlib_resources import path

from path import Path, TempDir

from dakara_feeder.dakara_feeder import DakaraFeeder
from dakara_feeder.metadata_parser import FFProbeMetadataParser


@skipUnless(FFProbeMetadataParser.is_available(), "FFProbe not installed")
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
        with TempDir() as temp:
            # copy required files
            with path("tests.resources.media", "dummy.ass") as file:
                Path(file).copy(temp)

            with path("tests.resources.media", "dummy.mkv") as file:
                Path(file).copy(temp)

            config = {"server": {}, "kara_folder": str(temp)}
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
                    "duration": 2.023,
                    "has_instrumental": True,
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
