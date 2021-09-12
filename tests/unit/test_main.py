from argparse import ArgumentParser, Namespace
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from dakara_base.config import ConfigNotFoundError
from dakara_base.exceptions import DakaraError
from path import Path

from dakara_feeder.__main__ import (
    create_config,
    feed_songs,
    feed_tags,
    feed_work_types,
    load_config_securely,
    load_feeder_securely,
    main,
)
from dakara_feeder.songs_feeder import SongsFeeder
from dakara_feeder.tags_feeder import TagsFeeder
from dakara_feeder.work_types_feeder import WorkTypesFeeder


class CreateConfigTestCase(TestCase):
    """Test the create-config subcommand"""

    @patch("dakara_feeder.__main__.CONFIG_FILE", "feeder.yaml")
    @patch("dakara_feeder.__main__.create_logger")
    @patch("dakara_feeder.__main__.create_config_file")
    def test_create_config(self, mocked_create_config_file, mocked_create_logger):
        """Test a normall config creation"""
        # call the function
        with self.assertLogs("dakara_feeder.__main__") as logger:
            create_config(Namespace(force=False))

        # assert the logs
        self.assertListEqual(
            logger.output,
            ["INFO:dakara_feeder.__main__:Please edit this file"],
        )

        # assert the call
        mocked_create_logger.assert_called_with(
            custom_log_format=ANY, custom_log_level=ANY
        )
        mocked_create_config_file.assert_called_with(
            "dakara_feeder.resources", "feeder.yaml", False
        )


class FeedSongsTestCase(TestCase):
    """Test the feed songs subcommand"""

    @patch.object(SongsFeeder, "feed")
    @patch("dakara_feeder.__main__.load_feeder_securely")
    @patch("dakara_feeder.__main__.load_config_securely")
    def test_feed(
        self,
        mocked_load_config,
        mocked_load_feeder,
        mocked_feed,
    ):
        """Test to feed songs"""
        # setup the mocks
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
        feed_songs(Namespace(debug=False, force=False, progress=True, prune=True))

        # assert the call
        mocked_load_config.assert_called_with(False)
        mocked_load_feeder.assert_called_with(ANY)
        mocked_feed.assert_called_with()


class FeedTagsTestCase(TestCase):
    """Test the feed tags subcommand"""

    @patch.object(TagsFeeder, "feed")
    @patch("dakara_feeder.__main__.load_feeder_securely")
    @patch("dakara_feeder.__main__.load_config_securely")
    def test_feed(
        self,
        mocked_load_config,
        mocked_load_feeder,
        mocked_feed,
    ):
        """Test to feed tags"""
        # setup the mocks
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
        feed_tags(
            Namespace(
                debug=False, file=Path("path") / "to" / "tags" / "file", progress=True
            )
        )

        # assert the call
        mocked_load_config.assert_called_with(False)
        mocked_load_feeder.assert_called_with(ANY)
        mocked_feed.assert_called_with()


class FeedWorkTypesTestCase(TestCase):
    """Test the feed work types subcommand"""

    @patch.object(WorkTypesFeeder, "feed")
    @patch("dakara_feeder.__main__.load_feeder_securely")
    @patch("dakara_feeder.__main__.load_config_securely")
    def test_feed(
        self,
        mocked_load_config,
        mocked_load_feeder,
        mocked_feed,
    ):
        """Test to feed work types"""
        # setup the mocks
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
        feed_work_types(
            Namespace(
                debug=False,
                file=Path("path") / "to" / "work_types" / "file",
                progress=True,
            )
        )

        # assert the call
        mocked_load_config.assert_called_with(False)
        mocked_load_feeder.assert_called_with(ANY)
        mocked_feed.assert_called_with()


class LoadConfigSafelyTestCase(TestCase):
    @patch("dakara_feeder.__main__.set_loglevel")
    @patch("dakara_feeder.__main__.load_config")
    @patch("dakara_feeder.__main__.get_config_file")
    @patch("dakara_feeder.__main__.create_logger")
    def test_load_config(
        self,
        mocked_create_logger,
        mocked_get_config_file,
        mocked_load_config,
        mocked_set_loglevel,
    ):
        """Test to load config"""
        # create the mocks
        config = {"key": "value"}
        mocked_get_config_file.return_value = Path("path") / "to" / "config"
        mocked_load_config.return_value = config

        # call the function
        config_loaded = load_config_securely()

        # assert the result
        self.assertEqual(config, config_loaded)

        # assert the call
        mocked_create_logger.assert_called_with(wrap=True)
        mocked_get_config_file.assert_called_with(ANY)
        mocked_load_config.assert_called_with(ANY, False, mandatory_keys=ANY)
        mocked_set_loglevel.assert_called_with(config)

    @patch("dakara_feeder.__main__.set_loglevel")
    @patch("dakara_feeder.__main__.load_config")
    @patch("dakara_feeder.__main__.get_config_file")
    @patch("dakara_feeder.__main__.create_logger")
    def test_load_config_error(
        self,
        mocked_create_logger,
        mocked_get_config_file,
        mocked_load_config,
        mocked_set_loglevel,
    ):
        """Test to load config when the file is not found"""
        # create the mocks
        mocked_get_config_file.return_value = Path("path") / "to" / "config"
        mocked_load_config.side_effect = ConfigNotFoundError("Config file not found")

        # call the function
        with self.assertRaisesRegex(
            ConfigNotFoundError,
            "Config file not found, please run 'dakara-feed create-config'",
        ):
            load_config_securely()

        # assert the call
        mocked_create_logger.assert_called_with(wrap=True)
        mocked_get_config_file.assert_called_with(ANY)
        mocked_load_config.assert_called_with(ANY, False, mandatory_keys=ANY)
        mocked_set_loglevel.assert_not_called()


class LoadFeederSafelyTestCase(TestCase):
    @patch("dakara_feeder.__main__.get_config_file")
    def test_load_feeder(
        self,
        mocked_get_config_file,
    ):
        """Test to load feeder"""
        # create the mocks
        feeder = MagicMock()
        mocked_get_config_file.return_value = Path("path") / "to" / "config"

        # call the function
        load_feeder_securely(feeder)

        # assert the call
        mocked_get_config_file.assert_not_called()
        feeder.load.assert_called_with()

    @patch("dakara_feeder.__main__.get_config_file")
    def test_load_feeder_error(
        self,
        mocked_get_config_file,
    ):
        """Test to load feeder when config file is incomplete"""
        # create the mocks
        feeder = MagicMock()
        feeder.load.side_effect = DakaraError("Any error message")
        mocked_get_config_file.return_value = Path("path") / "to" / "config"

        # call the function
        with self.assertRaises(DakaraError) as error:
            load_feeder_securely(feeder)

        # assert the error
        self.assertEqual(
            str(error.exception),
            "Any error message\nConfig may be incomplete, please check '{}'".format(
                Path("path") / "to" / "config"
            ),
        )

        # assert the call
        mocked_get_config_file.assert_called_with(ANY)


@patch("dakara_feeder.__main__.exit")
@patch.object(ArgumentParser, "parse_args")
class MainTestCase(TestCase):
    """Test the main action"""

    def test_normal_exit(self, mocked_parse_args, mocked_exit):
        """Test a normal exit"""
        # create mocks
        function = MagicMock()
        mocked_parse_args.return_value = Namespace(function=function, debug=False)

        # call the function
        main()

        # assert the call
        function.assert_called_with(ANY)
        mocked_exit.assert_called_with(0)

    def test_keyboard_interrupt(self, mocked_parse_args, mocked_exit):
        """Test a Ctrl+C exit"""
        # create mocks
        def function(args):
            raise KeyboardInterrupt()

        mocked_parse_args.return_value = Namespace(function=function, debug=False)

        # call the function
        with self.assertLogs("dakara_feeder.__main__", "DEBUG") as logger:
            main()

        # assert the call
        mocked_exit.assert_called_with(255)

        # assert the logs
        self.assertListEqual(
            logger.output, ["INFO:dakara_feeder.__main__:Quit by user"]
        )

    def test_known_error(self, mocked_parse_args, mocked_exit):
        """Test a known error exit"""
        # create mocks
        def function(args):
            raise DakaraError("error")

        mocked_parse_args.return_value = Namespace(function=function, debug=False)

        # call the function
        with self.assertLogs("dakara_feeder.__main__", "DEBUG") as logger:
            main()

        # assert the call
        mocked_exit.assert_called_with(1)

        # assert the logs
        self.assertListEqual(logger.output, ["CRITICAL:dakara_feeder.__main__:error"])

    def test_known_error_debug(self, mocked_parse_args, mocked_exit):
        """Test a known error exit in debug mode"""
        # create mocks
        def function(args):
            raise DakaraError("error message")

        mocked_parse_args.return_value = Namespace(function=function, debug=True)

        # call the function
        with self.assertRaisesRegex(DakaraError, "error message"):
            main()

        # assert the call
        mocked_exit.assert_not_called()

    def test_unknown_error(self, mocked_parse_args, mocked_exit):
        """Test an unknown error exit"""
        # create mocks
        def function(args):
            raise Exception("error")

        mocked_parse_args.return_value = Namespace(function=function, debug=False)

        # call the function
        with self.assertLogs("dakara_feeder.__main__", "DEBUG") as logger:
            main()

        # assert the call
        mocked_exit.assert_called_with(128)

        # assert the logs
        self.assertListEqual(
            logger.output,
            [
                ANY,
                "CRITICAL:dakara_feeder.__main__:Please fill a bug report at "
                "https://github.com/DakaraProject/dakara-feeder/issues",
            ],
        )

    def test_unknown_error_debug(self, mocked_parse_args, mocked_exit):
        """Test an unknown error exit in debug mode"""
        # create mocks
        def function(args):
            raise Exception("error message")

        mocked_parse_args.return_value = Namespace(function=function, debug=True)

        # call the function
        with self.assertRaisesRegex(Exception, "error message"):
            main()

        # assert the call
        mocked_exit.assert_not_called()
