from argparse import Namespace
from unittest import TestCase
from unittest.mock import patch

from path import Path

from dakara_feeder import config


@patch("dakara_feeder.config.CONFIG_FILE", "config.yaml")
class CreateConfigTestCase(TestCase):
    """Test the config file creator
    """

    @patch.object(Path, "copyfile")
    @patch.object(Path, "exists")
    def test_create_empty(self, mocked_exists, mocked_copyfile):
        """Test to create the config file in an empty directory
        """
        # setup mocks
        mocked_exists.return_value = False

        # call the function
        config.create_config(Namespace(force=False))

        # assert the call
        mocked_exists.assert_called_with()
        mocked_copyfile.assert_called_with(Path("config.yaml"))

    @patch("dakara_feeder.config.input")
    @patch.object(Path, "copyfile")
    @patch.object(Path, "exists")
    def test_create_existing_no(self, mocked_exists, mocked_copyfile, mocked_input):
        """Test to create the config file in a non empty directory
        """
        # setup mocks
        mocked_exists.return_value = True
        mocked_input.return_value("no")

        # call the function
        config.create_config(Namespace(force=False))

        # assert the call
        mocked_exists.assert_called_with()
        mocked_copyfile.assert_not_called()
        mocked_input.assert_called_with(
            "config.yaml already exists in this directory, overwrite? [y/N] "
        )

    @patch("dakara_feeder.config.input")
    @patch.object(Path, "copyfile")
    @patch.object(Path, "exists")
    def test_create_existing_invalid_input(
        self, mocked_exists, mocked_copyfile, mocked_input
    ):
        """Test to create the config file in a non empty directory with invalid input
        """
        # setup mocks
        mocked_exists.return_value = True
        mocked_input.return_value("")

        # call the function
        config.create_config(Namespace(force=False))

        # assert the call
        mocked_exists.assert_called_with()
        mocked_copyfile.assert_not_called()
        mocked_input.assert_called_with(
            "config.yaml already exists in this directory, overwrite? [y/N] "
        )

    @patch("dakara_feeder.config.input")
    @patch.object(Path, "copyfile")
    @patch.object(Path, "exists")
    def test_create_existing_force(self, mocked_exists, mocked_copyfile, mocked_input):
        """Test to create the config file in a non empty directory with force overwrite
        """
        # setup mocks
        mocked_exists.return_value = True
        mocked_input.return_value("no")

        # call the function
        config.create_config(Namespace(force=True))

        # assert the call
        mocked_exists.assert_not_called()
        mocked_copyfile.assert_called_with(Path("config.yaml"))
        mocked_input.assert_not_called()
