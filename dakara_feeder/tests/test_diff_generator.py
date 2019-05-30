from unittest import TestCase

from dakara_feeder import diff_generator


class DiffGeneratorTestCase(TestCase):
    """Test the diff generator
    """

    def test_generate_diff_all_added(self):
        """Test to generate diff when all files are added
        """
        added, deleted = diff_generator.generate_diff([], ["a", "b", "c"])

        self.assertCountEqual(["a", "b", "c"], added)
        self.assertCountEqual([], deleted)

    def test_generate_diff_all_deleted(self):
        """Test to generate diff when all files are deleted
        """
        added, deleted = diff_generator.generate_diff(["a", "b", "c"], [])

        self.assertCountEqual([], added)
        self.assertCountEqual(["a", "b", "c"], deleted)

    def test_generate_diff_no_diff(self):
        """Test to generate diff when nothing has changed
        """
        added, deleted = diff_generator.generate_diff(["a", "b", "c"], ["a", "b", "c"])

        self.assertCountEqual([], added)
        self.assertCountEqual([], deleted)

    def test_generate_diff(self):
        """Test to generate diff when some filse are added and some others deleted
        """
        added, deleted = diff_generator.generate_diff(["a", "b", "c"], ["d", "b", "a"])

        self.assertCountEqual(["d"], added)
        self.assertCountEqual(["c"], deleted)
