from argparse import ArgumentParser
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from path import Path

from dakara_base.exceptions import DakaraError
from dakara_base.config import ConfigNotFoundError
from dakara_feeder.commands.base import Subcommand


class SubcommandTestCase(TestCase):
    """Test the Subcommand class
    """

    class TestSubcommand(Subcommand):
        name = "name"
        description = "description"

        def set_subparser(self, subparser):
            subparser.add_argument("arg1")

        def handle(self, args):
            pass

    def test_init_base(self):
        """Test to instanciate the base abstract class
        """
        with self.assertRaises(TypeError):
            Subcommand()

    def test_init(self):
        """Test to instanciate a child class
        """
        self.TestSubcommand()

    def test_create_subparser(self):
        """Test to create a subparser
        """
        subcommand = self.TestSubcommand()
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        subcommand.create_subparser(subparsers)

        args = parser.parse_args(["name", "value"])

        self.assertEqual(args.arg1, "value")
        self.assertIs(args.function.__func__, subcommand.handle.__func__)

    def test_create_subparser_minimal(self):
        """Test to create a minimal subparser

        I.e. without settings its subperser.
        """

        class MinimalTestSubcommand(Subcommand):
            name = "name"
            description = "description"

            def handle(self, args):
                pass

        subcommand = MinimalTestSubcommand()
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        subcommand.create_subparser(subparsers)

        parser.parse_args(["name"])

    @patch("dakara_feeder.commands.base.set_loglevel")
    @patch("dakara_feeder.commands.base.load_config")
    @patch("dakara_feeder.commands.base.get_config_file")
    @patch("dakara_feeder.commands.base.create_logger")
    def test_load_config(
        self,
        mocked_create_logger,
        mocked_get_config_file,
        mocked_load_config,
        mocked_set_loglevel,
    ):
        """Test to load config
        """
        # create the mocks
        config = {"key": "value"}
        mocked_get_config_file.return_value = Path("path") / "to" / "config"
        mocked_load_config.return_value = config

        # call the function
        config_loaded = Subcommand.load_config()

        # assert the result
        self.assertEqual(config, config_loaded)

        # assert the call
        mocked_create_logger.assert_called_with(wrap=True)
        mocked_get_config_file.assert_called_with(ANY)
        mocked_load_config.assert_called_with(ANY, False, mandatory_keys=ANY)
        mocked_set_loglevel.assert_called_with(config)

    @patch("dakara_feeder.commands.base.set_loglevel")
    @patch("dakara_feeder.commands.base.load_config")
    @patch("dakara_feeder.commands.base.get_config_file")
    @patch("dakara_feeder.commands.base.create_logger")
    def test_load_config_error(
        self,
        mocked_create_logger,
        mocked_get_config_file,
        mocked_load_config,
        mocked_set_loglevel,
    ):
        """Test to load config when the file is not found
        """
        # create the mocks
        mocked_get_config_file.return_value = Path("path") / "to" / "config"
        mocked_load_config.side_effect = ConfigNotFoundError("Config file not found")

        # call the function
        with self.assertRaises(ConfigNotFoundError) as error:
            Subcommand.load_config()

        # assert the error
        self.assertEqual(
            str(error.exception),
            "Config file not found, please run 'dakara-feed create-config'",
        )

        # assert the call
        mocked_create_logger.assert_called_with(wrap=True)
        mocked_get_config_file.assert_called_with(ANY)
        mocked_load_config.assert_called_with(ANY, False, mandatory_keys=ANY)
        mocked_set_loglevel.assert_not_called()

    @patch("dakara_feeder.commands.base.get_config_file")
    def test_load_feeder(
        self, mocked_get_config_file,
    ):
        """Test to load feeder
        """
        # create the mocks
        feeder = MagicMock()
        mocked_get_config_file.return_value = Path("path") / "to" / "config"

        # call the function
        Subcommand.load_feeder(feeder)

        # assert the call
        mocked_get_config_file.assert_not_called()
        feeder.load.assert_called_with()

    @patch("dakara_feeder.commands.base.get_config_file")
    def test_load_feeder_error(
        self, mocked_get_config_file,
    ):
        """Test to load feeder when config file is incomplete
        """
        # create the mocks
        feeder = MagicMock()
        feeder.load.side_effect = DakaraError("Any error message")
        mocked_get_config_file.return_value = Path("path") / "to" / "config"

        # call the function
        with self.assertRaises(DakaraError) as error:
            Subcommand.load_feeder(feeder)

        # assert the error
        self.assertEqual(
            str(error.exception),
            "Any error message\nConfig may be incomplete, please check '{}'".format(
                Path("path") / "to" / "config"
            ),
        )

        # assert the call
        mocked_get_config_file.assert_called_with(ANY)
