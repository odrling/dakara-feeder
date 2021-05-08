from unittest import TestCase
from unittest.mock import ANY, patch

from dakara_feeder.subtitle_extractor import FFmpegSubtitleExtractor


class FFmpegSubtitleExtractorTestCase(TestCase):
    """Test the subtitle extractor based on FFmpeg
    """

    @patch("dakara_feeder.subtitle_extractor.subprocess.run")
    def test_is_available(self, mocked_run):
        """Test if the FFmpeg subtitle extractor is available
        """
        self.assertTrue(FFmpegSubtitleExtractor.is_available())
        mocked_run.assert_called_with(["ffmpeg", "-version"], stdout=ANY, stderr=ANY)

    @patch("dakara_feeder.subtitle_extractor.subprocess.run")
    def test_is_available_not_available(self, mocked_run):
        """Test if the FFmpeg subtitle extractor is not available
        """
        mocked_run.side_effect = FileNotFoundError()
        self.assertFalse(FFmpegSubtitleExtractor.is_available())
