from unittest import TestCase, skipUnless
from unittest.mock import patch

try:
    from importlib.resources import path

except ImportError:
    from importlib_resources import path

from path import Path, TempDir

from dakara_feeder.feeder.songs import SongsFeeder
from dakara_feeder.metadata import FFProbeMetadataParser


@skipUnless(FFProbeMetadataParser.is_available(), "FFProbe not installed")
@patch("dakara_feeder.feeder.songs.HTTPClientDakara", autoset=True)
class SongsFeederIntegrationTestCase(TestCase):
    """Integration tests for the SongsFeeder class."""

    def test_feed(self, mocked_http_client_dakara_class):
        """Test to feed."""
        # create the mocks
        mocked_http_client_dakara_class.return_value.retrieve_songs.return_value = []

        # create the object
        with TempDir() as temp:
            # copy required files
            with path("tests.resources.media", "dummy.ass") as file:
                Path(file).copy(temp)

            with path("tests.resources.media", "dummy.mkv") as file:
                Path(file).copy(temp)

            config = {"server": {}, "kara_folder": str(temp)}
            feeder = SongsFeeder(config, progress=False)

            # call the method
            with self.assertLogs("dakara_feeder.feeder.songs", "DEBUG"):
                with self.assertLogs("dakara_base.progress_bar"):
                    feeder.feed()

        # assert the mocked calls
        mocked_http_client_dakara_class.return_value.retrieve_songs.assert_called_with()
        mocked_http_client_dakara_class.return_value.post_song.assert_called_with(
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
