from unittest import TestCase

from path import Path

from dakara_feeder import diff_generator
from dakara_feeder.similarity_calculator import calculate_file_path_similarity


class GenerateDiffTestCase(TestCase):
    """Test the generate_diff method
    """

    def test_generate_diff_all_added(self):
        """Test to generate diff when all files are added
        """
        added, deleted, unchanged = diff_generator.generate_diff([], ["a", "b", "c"])

        self.assertCountEqual(["a", "b", "c"], added)
        self.assertCountEqual([], deleted)
        self.assertCountEqual([], unchanged)

    def test_generate_diff_all_deleted(self):
        """Test to generate diff when all files are deleted
        """
        added, deleted, unchanged = diff_generator.generate_diff(["a", "b", "c"], [])

        self.assertCountEqual([], added)
        self.assertCountEqual(["a", "b", "c"], deleted)
        self.assertCountEqual([], unchanged)

    def test_generate_diff_no_diff(self):
        """Test to generate diff when nothing has changed
        """
        added, deleted, unchanged = diff_generator.generate_diff(
            ["a", "b", "c"], ["a", "b", "c"]
        )

        self.assertCountEqual([], added)
        self.assertCountEqual([], deleted)
        self.assertCountEqual(["a", "b", "c"], unchanged)

    def test_generate_diff(self):
        """Test to generate diff when some filse are added and some others deleted
        """
        added, deleted, unchanged = diff_generator.generate_diff(
            ["a", "b", "c"], ["d", "b", "a"]
        )

        self.assertCountEqual(["d"], added)
        self.assertCountEqual(["c"], deleted)
        self.assertCountEqual(["a", "b"], unchanged)


class MatchSimilarTestCase(TestCase):
    """Test match_similar method
    """

    def test_simple(self):
        """Test basic similar name matching
        """

        list1 = [
            Path("directory/file.mp4"),
            Path("directory/other.mp4"),
            Path("other/file.mp4"),
            Path("directory/newfile.mkv"),
        ]

        list2 = [
            Path("directory/fil.mp4"),
            Path("other/other.mp4"),
            Path("other/fil.mp4"),
            Path("directory/oldfile.mkv"),
        ]

        similar, remaining1, remaining2 = diff_generator.match_similar(
            list1, list2, calculate_file_path_similarity
        )

        self.assertCountEqual(
            similar,
            [
                ("directory/file.mp4", "directory/fil.mp4"),
                ("other/file.mp4", "other/fil.mp4"),
                ("directory/other.mp4", "other/other.mp4"),
            ],
        )
        self.assertCountEqual(remaining1, ["directory/newfile.mkv"])
        self.assertCountEqual(remaining2, ["directory/oldfile.mkv"])
