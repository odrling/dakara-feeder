from unittest import TestCase

from dakara_feeder import utils


class DivideChuncksTestCase(TestCase):
    """Test the function to divide in chuncks."""

    def test(self):
        """Test to divide an array of integers."""
        items = [34, 58, 98, 35, 45]
        chuncks = list(utils.divide_chunks(items, 2))

        self.assertEqual(len(chuncks), 3)
        self.assertListEqual(chuncks, [[34, 58], [98, 35], [45]])


class CleanDictTestCase(TestCase):
    """ "Test the function to clean dictionary."""

    def test(self):
        """Test to clean a dictionary."""
        target = {"a": 1, "b": 2, "c": 3}
        target_clean = utils.clean_dict(target, ["a", "c", "d"])

        self.assertDictEqual(target_clean, {"a": 1, "c": 3})
