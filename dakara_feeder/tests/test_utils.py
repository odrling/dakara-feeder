from unittest import TestCase

from dakara_feeder import utils


class DivideChuncksTestCase(TestCase):
    """Test the function to divide in chuncks
    """

    def test(self):
        """Test a simple case
        """
        items = [34, 58, 98, 35, 45]
        chuncks = list(utils.divide_chunks(items, 2))

        self.assertEqual(len(chuncks), 3)
        self.assertListEqual(chuncks, [[34, 58], [98, 35], [45]])
