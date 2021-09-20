"""Command line interface to run the feeder."""

import logging
from argparse import ArgumentParser

from dakara_base.config import (
    ConfigNotFoundError,
    create_config_file,
    create_logger,
    get_config_file,
    load_config,
    set_loglevel,
)
from dakara_base.exceptions import DakaraError
from path import Path

from dakara_feeder.songs_feeder import SongsFeeder
from dakara_feeder.tags_feeder import TagsFeeder
from dakara_feeder.version import __date__, __version__
from dakara_feeder.work_types_feeder import WorkTypesFeeder

CONFIG_FILE = "feeder.yaml"


logger = logging.getLogger(__name__)


def get_parser():
    """Get the parser.

    Returns:
        argparse.ArgumentParser: Parser.
    """
    # main parser
    parser = ArgumentParser(
        prog="dakara-feeder", description="Feeder for the Dakara project"
    )

    parser.set_defaults(function=lambda _: parser.print_help())

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="enable debug output, increase verbosity",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {} ({})".format(__version__, __date__),
    )

    # subparsers
    subparser = parser.add_subparsers(title="subcommands")

    # feed subparser
    feed_parser = subparser.add_parser(
        "feed",
        description="Feed data to the server",
        help="Feed data to the server",
    )

    feed_parser.add_argument(
        "--no-progress",
        dest="progress",
        action="store_false",
        help="do not display progress bars",
    )

    # create config subparser
    create_config_subparser = subparser.add_parser(
        "create-config",
        description="Create a new config file in user directory",
        help="Create a new config file in user directory",
    )
    create_config_subparser.set_defaults(function=create_config)

    create_config_subparser.add_argument(
        "--force",
        help="overwrite previous config file if it exists",
        action="store_true",
    )

    # feed subparsers
    feed_subparser = feed_parser.add_subparsers(title="feeds")

    # feed songs subparser
    songs_subparser = feed_subparser.add_parser(
        "songs",
        description="Feed songs to the server",
        help="Feed songs to the server",
    )
    songs_subparser.set_defaults(function=feed_songs)

    songs_subparser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="force unchanged files to be updated",
    )

    songs_subparser.add_argument(
        "--no-prune",
        dest="prune",
        action="store_false",
        help="do not delete artists and works without songs at end of feed",
    )

    # feed tags subparser
    tags_subparser = feed_subparser.add_parser(
        "tags",
        description="Feed tags to the server",
        help="Feed tags to the server",
    )
    tags_subparser.set_defaults(function=feed_tags)

    tags_subparser.add_argument(
        "file",
        help="path to the tags configuration file",
        type=Path,
    )

    # feed work types subparser
    work_types_subparser = feed_subparser.add_parser(
        "work-types",
        description="Feed work types to the server",
        help="Feed work types to the server",
    )
    work_types_subparser.set_defaults(function=feed_work_types)

    work_types_subparser.add_argument(
        "file",
        help="path to the work types configuration file",
        type=Path,
    )

    return parser


def create_config(args):
    """Create the config.

    Args:
        args (argparse.Namespace): Arguments from command line.
    """
    create_logger(custom_log_format="%(message)s", custom_log_level="INFO")
    create_config_file("dakara_feeder.resources", CONFIG_FILE, args.force)
    logger.info("Please edit this file")


def feed_songs(args):
    """Feed songs.

    Args:
        args (argparse.Namespace): Arguments from command line.
    """
    config = load_config_securely(args.debug)
    feeder = SongsFeeder(
        config, force_update=args.force, prune=args.prune, progress=args.progress
    )
    load_feeder_securely(feeder)
    feeder.feed()


def feed_tags(args):
    """Feed tags.

    Args:
        args (argparse.Namespace): Arguments from command line.
    """
    config = load_config_securely(args.debug)
    feeder = TagsFeeder(config, tags_file_path=args.file, progress=args.progress)
    load_feeder_securely(feeder)
    feeder.feed()


def feed_work_types(args):
    """Feed work types.

    Args:
        args (argparse.Namespace): Arguments from command line.
    """
    config = load_config_securely(args.debug)
    feeder = WorkTypesFeeder(
        config, work_types_file_path=args.file, progress=args.progress
    )
    load_feeder_securely(feeder)
    feeder.feed()


def load_config_securely(debug=False):
    """Securely load the config.

    Display help to create config if it fails.

    Args:
        debug (bool): enable debug mode.

    Returns:
        dict: config values.

    Raises:
        ConfigNotFoundError: If loading the config raises the same error.
    """
    create_logger(wrap=True)

    try:
        config = load_config(
            get_config_file(CONFIG_FILE),
            debug,
            mandatory_keys=["kara_folder", "server"],
        )

    except ConfigNotFoundError as error:
        raise ConfigNotFoundError(
            "{}, please run 'dakara-feed create-config'".format(error)
        ) from error

    set_loglevel(config)

    return config


def load_feeder_securely(feeder):
    """Securely load the feeder.

    Consider that the config is incomplete if it fails.

    Raises:
        DakaraError: If loading the feeder raises an equivalent error.
    """
    try:
        feeder.load()

    except DakaraError as error:
        raise error.__class__(
            "{}\nConfig may be incomplete, please check '{}'".format(
                error, get_config_file(CONFIG_FILE)
            )
        ) from error


def main():
    """Main command."""
    parser = get_parser()
    args = parser.parse_args()

    try:
        args.function(args)
        value = 0

    except KeyboardInterrupt:
        logger.info("Quit by user")
        value = 255

    except DakaraError as error:
        if args.debug:
            raise

        logger.critical(error)
        value = 1

    except BaseException as error:
        if args.debug:
            raise

        logger.exception("Unexpected error: %s", error)
        logger.critical(
            "Please fill a bug report at "
            "https://github.com/DakaraProject/dakara-feeder/issues"
        )
        value = 128

    exit(value)
