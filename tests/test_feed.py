from argparse import ArgumentParser, Namespace
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from dakara_base.config import ConfigNotFoundError
from dakara_base.exceptions import DakaraError
from path import Path

from dakara_feeder import DakaraFeeder
from dakara_feeder.commands import feed


class GetParserTestCase(TestCase):
    """Test the parser creator
    """

    def test(self):
        """Test a parser is created
        """
        parser = feed.get_parser()
        self.assertIsNotNone(parser)

    def test_main_function(self):
        """Test the parser calls feed by default
        """
        # call the function
        parser = feed.get_parser()
        args = parser.parse_args([])

        # check the function
        self.assertIs(args.function, feed.feed)

    def test_create_config_function(self):
        """Test the parser calls create_config when prompted
        """
        # call the function
        parser = feed.get_parser()
        args = parser.parse_args(["create-config"])

        # check the function
        self.assertIs(args.function, feed.create_config)


class FeedTestCase(TestCase):
    """Test the feed action
    """

    @patch.object(DakaraFeeder, "feed")
    @patch.object(DakaraFeeder, "load")
    @patch("dakara_feeder.commands.feed.load_config")
    @patch("dakara_feeder.commands.feed.get_config_file")
    @patch("dakara_feeder.commands.feed.create_logger")
    def test_feed_config_not_found(
        self,
        mocked_create_logger,
        mocked_get_config_file,
        mocked_load_config,
        mocked_load,
        mocked_feed,
    ):
        """Test when config file is not found
        """
        # create the mocks
        mocked_get_config_file.return_value = Path("path") / "to" / "config"
        mocked_load_config.side_effect = ConfigNotFoundError("Config file not found")

        # call the function
        with self.assertRaisesRegex(
            ConfigNotFoundError,
            "Config file not found, please run 'dakara-feed create-config'",
        ):
            feed.feed(Namespace(debug=False, force=False, progress=True))

        # assert the call
        mocked_load.assert_not_called()
        mocked_feed.assert_not_called()

    @patch.object(DakaraFeeder, "feed")
    @patch.object(DakaraFeeder, "load")
    @patch("dakara_feeder.commands.feed.set_loglevel")
    @patch("dakara_feeder.commands.feed.load_config")
    @patch("dakara_feeder.commands.feed.get_config_file")
    @patch("dakara_feeder.commands.feed.create_logger")
    def test_feed_config_incomplete(
        self,
        mocked_create_logger,
        mocked_get_config_file,
        mocked_load_config,
        mocked_set_loglevel,
        mocked_load,
        mocked_feed,
    ):
        """Test when config file is incomplete
        """
        # create the mocks
        mocked_get_config_file.return_value = Path("path") / "to" / "config"
        mocked_load.side_effect = DakaraError("Config-related error")
        config = {
            "kara_folder": Path("path") / "to" / "folder",
            "server": {
                "url": "www.example.com",
                "login": "login",
                "password": "password",
            },
        }
        mocked_load_config.return_value = config

        # call the function
        with self.assertRaisesRegex(DakaraError, "Config-related error"):
            with self.assertLogs("dakara_feeder.commands.feed") as logger:
                feed.feed(Namespace(debug=False, force=False, progress=True))

        # assert the logs
        self.assertListEqual(
            logger.output,
            [
                "WARNING:dakara_feeder.commands.feed:Config may be incomplete, "
                "please check '{}'".format(Path("path") / "to" / "config")
            ],
        )

        # assert the call
        mocked_load.assert_called_with()
        mocked_feed.assert_not_called()

    @patch.object(DakaraFeeder, "feed")
    @patch.object(DakaraFeeder, "load")
    @patch("dakara_feeder.commands.feed.set_loglevel")
    @patch("dakara_feeder.commands.feed.load_config")
    @patch("dakara_feeder.commands.feed.get_config_file")
    @patch("dakara_feeder.commands.feed.create_logger")
    def test_feed(
        self,
        mocked_create_logger,
        mocked_get_config_file,
        mocked_load_config,
        mocked_set_loglevel,
        mocked_load,
        mocked_feed,
    ):
        """Test a simple feed action
        """
        # setup the mocks
        mocked_get_config_file.return_value = Path("path") / "to" / "config"
        config = {
            "kara_folder": Path("path") / "to" / "folder",
            "server": {
                "url": "www.example.com",
                "login": "login",
                "password": "password",
            },
        }
        mocked_load_config.return_value = config

        # call the function
        feed.feed(Namespace(debug=False, force=False, progress=True))

        # assert the call
        mocked_create_logger.assert_called_with(wrap=True)
        mocked_load_config.assert_called_with(
            Path("path") / "to" / "config",
            False,
            mandatory_keys=["kara_folder", "server"],
        )
        mocked_set_loglevel.assert_called_with(config)
        mocked_load.assert_called_with()
        mocked_feed.assert_called_with()


class CreateConfigTestCase(TestCase):
    """Test the create-config action
    """

    @patch("dakara_feeder.commands.feed.create_logger")
    @patch("dakara_feeder.commands.feed.create_config_file")
    def test_create_config(self, mocked_create_config_file, mocked_create_logger):
        """Test a normall config creation
        """
        # call the function
        with self.assertLogs("dakara_feeder.commands.feed") as logger:
            feed.create_config(Namespace(force=False))

        # assert the logs
        self.assertListEqual(
            logger.output, ["INFO:dakara_feeder.commands.feed:Please edit this file"]
        )

        # assert the call
        mocked_create_logger.assert_called_with(
            custom_log_format=ANY, custom_log_level=ANY
        )
        mocked_create_config_file.assert_called_with(
            "dakara_feeder.resources", "feeder.yaml", False
        )


@patch("dakara_feeder.commands.feed.exit")
@patch.object(ArgumentParser, "parse_args")
class MainTestCase(TestCase):
    """Test the main action
    """

    def test_normal_exit(self, mocked_parse_args, mocked_exit):
        """Test a normal exit
        """
        # create mocks
        function = MagicMock()
        mocked_parse_args.return_value = Namespace(function=function, debug=False)

        # call the function
        feed.main()

        # assert the call
        function.assert_called_with(ANY)
        mocked_exit.assert_called_with(0)

    def test_keyboard_interrupt(self, mocked_parse_args, mocked_exit):
        """Test a Ctrl+C exit
        """
        # create mocks
        def function(args):
            raise KeyboardInterrupt()

        mocked_parse_args.return_value = Namespace(function=function, debug=False)

        # call the function
        with self.assertLogs("dakara_feeder.commands.feed", "DEBUG") as logger:
            feed.main()

        # assert the call
        mocked_exit.assert_called_with(255)

        # assert the logs
        self.assertListEqual(
            logger.output, ["INFO:dakara_feeder.commands.feed:Quit by user"]
        )

    def test_known_error(self, mocked_parse_args, mocked_exit):
        """Test a known error exit
        """
        # create mocks
        def function(args):
            raise DakaraError("error")

        mocked_parse_args.return_value = Namespace(function=function, debug=False)

        # call the function
        with self.assertLogs("dakara_feeder.commands.feed", "DEBUG") as logger:
            feed.main()

        # assert the call
        mocked_exit.assert_called_with(1)

        # assert the logs
        self.assertListEqual(
            logger.output, ["CRITICAL:dakara_feeder.commands.feed:error"]
        )

    def test_known_error_debug(self, mocked_parse_args, mocked_exit):
        """Test a known error exit in debug mode
        """
        # create mocks
        def function(args):
            raise DakaraError("error")

        mocked_parse_args.return_value = Namespace(function=function, debug=True)

        # call the function
        with self.assertRaisesRegex(DakaraError, "error"):
            feed.main()

        # assert the call
        mocked_exit.assert_not_called()

    def test_unknown_error(self, mocked_parse_args, mocked_exit):
        """Test an unknown error exit
        """
        # create mocks
        def function(args):
            raise Exception("error")

        mocked_parse_args.return_value = Namespace(function=function, debug=False)

        # call the function
        with self.assertLogs("dakara_feeder.commands.feed", "DEBUG") as logger:
            feed.main()

        # assert the call
        mocked_exit.assert_called_with(128)

        # assert the logs
        self.assertListEqual(
            logger.output,
            [
                ANY,
                "CRITICAL:dakara_feeder.commands.feed:Please fill a bug report at "
                "https://github.com/DakaraProject/dakara-feeder/issues",
            ],
        )

    def test_unknown_error_debug(self, mocked_parse_args, mocked_exit):
        """Test an unknown error exit in debug mode
        """
        # create mocks
        def function(args):
            raise Exception("error")

        mocked_parse_args.return_value = Namespace(function=function, debug=True)

        # call the function
        with self.assertRaisesRegex(Exception, "error"):
            feed.main()

        # assert the call
        mocked_exit.assert_not_called()
