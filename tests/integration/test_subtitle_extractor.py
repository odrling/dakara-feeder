from unittest import TestCase, skipUnless

from path import Path

try:
    from importlib.resources import path

except ImportError:
    from importlib_resources import path

from dakara_feeder.subtitle_extractor import FFmpegSubtitleExtractor


@skipUnless(FFmpegSubtitleExtractor.is_available(), "FFmpeg not installed")
class FFmpegSubtitleExtractorTestCase(TestCase):
    """Test the subtitle extractor based on FFmpeg in an integrated way
    """

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
