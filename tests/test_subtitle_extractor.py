from unittest import TestCase
from unittest.mock import ANY, patch

from path import Path

try:
    from importlib.resources import path

except ImportError:
    from importlib_resources import path

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

    def test_extract(self):
        """Test to extract subtitle from file
        """
        with path("tests.resources.media", "dummy.mkv") as file:
            extractor = FFmpegSubtitleExtractor.extract(Path(file))
            subtitle = extractor.get_subtitle()

        with path("tests.resources.subtitles", "dummy.ass") as file:
            subtitle_expected = file.read_text()

        self.assertEqual(subtitle, subtitle_expected)

    def test_extract_error(self):
        """Test error when extracting subtitle from file
        """
        file_path = Path("nowhere")
        extractor = FFmpegSubtitleExtractor.extract(file_path)
        subtitle = extractor.get_subtitle()

        self.assertEqual(subtitle, "")
