from argparse import ArgumentParser, Namespace
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from dakara_base.exceptions import DakaraError
from path import Path

from dakara_feeder import feed
from dakara_feeder.dakara_feeder import DakaraFeeder


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
    @patch("dakara_feeder.feed.set_loglevel")
    @patch("dakara_feeder.feed.load_config")
    @patch("dakara_feeder.feed.create_logger")
    def test_feed(
        self,
        mocked_create_logger,
        mocked_load_config,
        mocked_set_loglevel,
        mocked_load,
        mocked_feed,
    ):
        """Test a simple feed action
        """
        # setup the mocks
        config = {
            "kara_folder": Path("path/to/folder"),
            "server": {
                "url": "www.example.com",
                "login": "login",
                "password": "password",
            },
        }
        mocked_load_config.return_value = config

        # call the function
        feed.feed(
            Namespace(config="config.yaml", debug=False, force=False, progress=True)
        )

        # assert the call
        mocked_create_logger.assert_called_with(wrap=True)
        mocked_load_config.assert_called_with(
            Path("config.yaml"), False, mandatory_keys=["kara_folder", "server"]
        )
        mocked_set_loglevel.assert_called_with(config)
        mocked_load.assert_called_with()
        mocked_feed.assert_called_with()


class MainTestCase(TestCase):
    """Test the main action
    """

    @patch("dakara_feeder.feed.exit")
    @patch.object(ArgumentParser, "parse_args")
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

    @patch("dakara_feeder.feed.exit")
    @patch.object(ArgumentParser, "parse_args")
    def test_keyboard_interrupt(self, mocked_parse_args, mocked_exit):
        """Test a Ctrl+C exit
        """
        # create mocks
        def function(args):
            raise KeyboardInterrupt()

        mocked_parse_args.return_value = Namespace(function=function, debug=False)

        # call the function
        with self.assertLogs("dakara_feeder.feed", "DEBUG") as logger:
            feed.main()

        # assert the call
        mocked_exit.assert_called_with(255)

        # assert the logs
        self.assertListEqual(logger.output, ["INFO:dakara_feeder.feed:Quit by user"])

    @patch("dakara_feeder.feed.exit")
    @patch.object(ArgumentParser, "parse_args")
    def test_known_error(self, mocked_parse_args, mocked_exit):
        """Test a known error exit
        """
        # create mocks
        def function(args):
            raise DakaraError("error")

        mocked_parse_args.return_value = Namespace(function=function, debug=False)

        # call the function
        with self.assertLogs("dakara_feeder.feed", "DEBUG") as logger:
            feed.main()

        # assert the call
        mocked_exit.assert_called_with(1)

        # assert the logs
        self.assertListEqual(logger.output, ["CRITICAL:dakara_feeder.feed:error"])

    @patch("dakara_feeder.feed.exit")
    @patch.object(ArgumentParser, "parse_args")
    def test_known_error_debug(self, mocked_parse_args, mocked_exit):
        """Test a known error exit in debug mode
        """
        # create mocks
        def function(args):
            raise DakaraError("error")

        mocked_parse_args.return_value = Namespace(function=function, debug=True)

        # call the function
        with self.assertRaises(DakaraError) as error:
            feed.main()

        # assert the call
        mocked_exit.assert_not_called()

        # assert the error
        self.assertEqual(str(error.exception), "error")

    @patch("dakara_feeder.feed.exit")
    @patch.object(ArgumentParser, "parse_args")
    def test_unknown_error(self, mocked_parse_args, mocked_exit):
        """Test an unknown error exit
        """
        # create mocks
        def function(args):
            raise Exception("error")

        mocked_parse_args.return_value = Namespace(function=function, debug=False)

        # call the function
        with self.assertLogs("dakara_feeder.feed", "DEBUG") as logger:
            feed.main()

        # assert the call
        mocked_exit.assert_called_with(128)

        # assert the logs
        self.assertListEqual(
            logger.output,
            [
                ANY,
                "CRITICAL:dakara_feeder.feed:Please fill a bug report at "
                "https://github.com/DakaraProject/dakara-feeder/issues",
            ],
        )

    @patch("dakara_feeder.feed.exit")
    @patch.object(ArgumentParser, "parse_args")
    def test_unknown_error_debug(self, mocked_parse_args, mocked_exit):
        """Test an unknown error exit in debug mode
        """
        # create mocks
        def function(args):
            raise Exception("error")

        mocked_parse_args.return_value = Namespace(function=function, debug=True)

        # call the function
        with self.assertRaises(Exception) as error:
            feed.main()

        # assert the call
        mocked_exit.assert_not_called()

        # assert the error
        self.assertEqual(str(error.exception), "error")
