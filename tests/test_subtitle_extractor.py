from unittest import TestCase
from unittest.mock import ANY, patch

from dakara_base.resources_manager import get_file
from path import Path

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
        file_path = get_file("tests.resources.media", "dummy.mkv")
        extractor = FFmpegSubtitleExtractor.extract(file_path)
        subtitle = extractor.get_subtitle()

        subtitle_path = get_file("tests.resources.subtitles", "dummy.ass")
        subtitle_expected = subtitle_path.text()

        self.assertEqual(subtitle, subtitle_expected)

    def test_extract_error(self):
        """Test error when extracting subtitle from file
        """
        file_path = Path("nowhere")
        extractor = FFmpegSubtitleExtractor.extract(file_path)
        subtitle = extractor.get_subtitle()

        self.assertEqual(subtitle, "")
