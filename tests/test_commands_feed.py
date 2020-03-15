from argparse import ArgumentParser, Namespace
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from dakara_base.exceptions import DakaraError
from dakara_feeder.commands import feed
from dakara_feeder.commands.create_config import CreateConfigSubcommand


class GetSubcommandsTestCase(TestCase):
    """Test the get_subcommands function
    """

    def test_get(self):
        """Test to get subcommands

        No mock involved. Test if at least the CreateConfigSubcommand exists.
        """
        subcommands = feed.get_subcommands()
        self.assertIn(CreateConfigSubcommand, subcommands)


class GetParserTestCase(TestCase):
    """Test the get_parser function
    """

    def test(self):
        """Test a parser is created
        """
        parser = feed.get_parser()
        self.assertIsNotNone(parser)


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
        with self.assertRaises(DakaraError) as error:
            feed.main()

        # assert the call
        mocked_exit.assert_not_called()

        # assert the error
        self.assertEqual(str(error.exception), "error")

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
        with self.assertRaises(Exception) as error:
            feed.main()

        # assert the call
        mocked_exit.assert_not_called()

        # assert the error
        self.assertEqual(str(error.exception), "error")
