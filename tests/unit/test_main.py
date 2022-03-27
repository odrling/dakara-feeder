from argparse import ArgumentParser, Namespace
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from dakara_base.config import Config
from path import Path

from dakara_feeder.__main__ import (
    create_config,
    feed_songs,
    feed_tags,
    feed_work_types,
    feed_works,
    main,
)


@patch("dakara_feeder.__main__.CONFIG_FILE", "feeder.yaml")
@patch("dakara_feeder.__main__.create_logger")
@patch("dakara_feeder.__main__.create_config_file")
class CreateConfigTestCase(TestCase):
    """Test the create-config subcommand."""

    def test_create_config(self, mocked_create_config_file, mocked_create_logger):
        """Test a normall config creation."""
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


@patch("dakara_feeder.__main__.SongsFeeder", autospec=True)
@patch("dakara_feeder.__main__.set_loglevel")
@patch.object(Config, "set_debug")
@patch.object(Config, "check_mandatory_keys")
@patch.object(Config, "load_file")
@patch("dakara_feeder.__main__.create_logger")
class FeedSongsTestCase(TestCase):
    """Test the feed songs subcommand."""

    def test_feed(
        self,
        mocked_create_logger,
        mocked_load_file,
        mocked_check_mandatory_keys,
        mocked_set_debug,
        mocked_set_loglevel,
        mocked_songs_feeder_class,
    ):
        """Test to feed songs."""
        # call the function
        feed_songs(Namespace(debug=False, force=False, progress=True, prune=True))

        # assert the call
        mocked_create_logger.assert_called_with(wrap=True)
        mocked_load_file.assert_called_with(ANY)
        mocked_check_mandatory_keys.assert_called_with(["kara_folder", "server"])
        mocked_set_debug.assert_called_with(False)
        mocked_set_loglevel.assert_called_with(ANY)
        mocked_songs_feeder_class.assert_called_with(
            ANY, force_update=False, prune=True, progress=True
        )
        mocked_songs_feeder_class.return_value.load.assert_called_with()
        mocked_songs_feeder_class.return_value.feed.assert_called_with()


@patch("dakara_feeder.__main__.WorksFeeder", autospec=True)
@patch("dakara_feeder.__main__.set_loglevel")
@patch.object(Config, "set_debug")
@patch.object(Config, "check_mandatory_keys")
@patch.object(Config, "load_file")
@patch("dakara_feeder.__main__.create_logger")
class FeedWorksTestCase(TestCase):
    """Test the feed works subcommand."""

    def test_feed(
        self,
        mocked_create_logger,
        mocked_load_file,
        mocked_check_mandatory_keys,
        mocked_set_debug,
        mocked_set_loglevel,
        mocked_works_feeder_class,
    ):
        """Test to feed songs."""
        # call the function
        feed_works(
            Namespace(
                debug=False,
                file=Path("path") / "to" / "file",
                progress=True,
                update_only=False,
            )
        )

        # assert the call
        mocked_create_logger.assert_called_with(wrap=True)
        mocked_load_file.assert_called_with(ANY)
        mocked_check_mandatory_keys.assert_called_with(["server"])
        mocked_set_debug.assert_called_with(False)
        mocked_set_loglevel.assert_called_with(ANY)
        mocked_works_feeder_class.assert_called_with(
            ANY,
            works_file_path=Path("path") / "to" / "file",
            progress=True,
            update_only=False,
        )
        mocked_works_feeder_class.return_value.load.assert_called_with()
        mocked_works_feeder_class.return_value.feed.assert_called_with()


@patch("dakara_feeder.__main__.TagsFeeder", autospec=True)
@patch("dakara_feeder.__main__.set_loglevel")
@patch.object(Config, "set_debug")
@patch.object(Config, "check_mandatory_keys")
@patch.object(Config, "load_file")
@patch("dakara_feeder.__main__.create_logger")
class FeedTagsTestCase(TestCase):
    """Test the feed tags subcommand."""

    def test_feed(
        self,
        mocked_create_logger,
        mocked_load_file,
        mocked_check_mandatory_keys,
        mocked_set_debug,
        mocked_set_loglevel,
        mocked_tags_feeder_class,
    ):
        """Test to feed tags."""
        # call the function
        feed_tags(
            Namespace(debug=False, file=Path("path") / "to" / "file", progress=True)
        )

        # assert the call
        mocked_create_logger.assert_called_with(wrap=True)
        mocked_load_file.assert_called_with(ANY)
        mocked_check_mandatory_keys.assert_called_with(["server"])
        mocked_set_debug.assert_called_with(False)
        mocked_set_loglevel.assert_called_with(ANY)
        mocked_tags_feeder_class.assert_called_with(
            ANY, tags_file_path=Path("path") / "to" / "file", progress=True
        )
        mocked_tags_feeder_class.return_value.load.assert_called_with()
        mocked_tags_feeder_class.return_value.feed.assert_called_with()


@patch("dakara_feeder.__main__.WorkTypesFeeder", autospec=True)
@patch("dakara_feeder.__main__.set_loglevel")
@patch.object(Config, "set_debug")
@patch.object(Config, "check_mandatory_keys")
@patch.object(Config, "load_file")
@patch("dakara_feeder.__main__.create_logger")
class FeedWorkTypesTestCase(TestCase):
    """Test the feed work types subcommand."""

    def test_feed(
        self,
        mocked_create_logger,
        mocked_load_file,
        mocked_check_mandatory_keys,
        mocked_set_debug,
        mocked_set_loglevel,
        mocked_work_types_feeder_class,
    ):
        """Test to feed work types."""
        # call the function
        feed_work_types(
            Namespace(
                debug=False,
                file=Path("path") / "to" / "file",
                progress=True,
            )
        )

        # assert the call
        mocked_create_logger.assert_called_with(wrap=True)
        mocked_load_file.assert_called_with(ANY)
        mocked_check_mandatory_keys.assert_called_with(["server"])
        mocked_set_debug.assert_called_with(False)
        mocked_set_loglevel.assert_called_with(ANY)
        mocked_work_types_feeder_class.assert_called_with(
            ANY, work_types_file_path=Path("path") / "to" / "file", progress=True
        )
        mocked_work_types_feeder_class.return_value.load.assert_called_with()
        mocked_work_types_feeder_class.return_value.feed.assert_called_with()


@patch("dakara_feeder.__main__.sys.exit")
@patch.object(ArgumentParser, "parse_args")
class MainTestCase(TestCase):
    """Test the main action."""

    def test_normal_exit(self, mocked_parse_args, mocked_exit):
        """Test a normal exit."""
        # create mocks
        function = MagicMock()
        mocked_parse_args.return_value = Namespace(function=function, debug=False)

        # call the function
        main()

        # assert the call
        function.assert_called_with(ANY)
        mocked_exit.assert_called_with(0)
