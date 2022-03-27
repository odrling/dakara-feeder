"""Command line interface to run the feeder."""

import logging
import sys
from argparse import ArgumentParser

from dakara_base.config import (
    Config,
    ConfigNotFoundError,
    create_config_file,
    create_logger,
    set_loglevel,
)
from dakara_base.directory import directories
from dakara_base.exceptions import (
    DakaraError,
    generate_exception_handler,
    handle_all_exceptions,
)
from path import Path

from dakara_feeder.feeder.songs import SongsFeeder
from dakara_feeder.feeder.tags import TagsFeeder
from dakara_feeder.feeder.work_types import WorkTypesFeeder
from dakara_feeder.feeder.works import WorksFeeder
from dakara_feeder.version import __date__, __version__

CONFIG_FILE = "feeder.yaml"
CONFIG_PREFIX = "DAKARA"


logger = logging.getLogger(__name__)
handle_config_not_found = generate_exception_handler(
    ConfigNotFoundError, "Please run 'dakara-feeder create-config'"
)
handle_config_incomplete = generate_exception_handler(
    DakaraError,
    "Config may be incomplete, please check '{}'".format(
        directories.user_config_dir / CONFIG_FILE
    ),
)


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

    # feed works subparser
    works_subparser = feed_subparser.add_parser(
        "works",
        description="Feed works to the server",
        help="Feed works to the server",
    )
    works_subparser.set_defaults(function=feed_works)

    works_subparser.add_argument(
        "file",
        help="path to the works JSON file",
        type=Path,
    )

    works_subparser.add_argument(
        "-u",
        "--update-only",
        help="only update existing works on the server",
        action="store_true",
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
    """Create a new config file.

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
    with handle_config_not_found():
        create_logger(wrap=True)
        config = Config(CONFIG_PREFIX)
        config.load_file(directories.user_config_dir / CONFIG_FILE)
        config.check_mandatory_keys(["kara_folder", "server"])
        config.set_debug(args.debug)
        set_loglevel(config)

    feeder = SongsFeeder(
        config, force_update=args.force, prune=args.prune, progress=args.progress
    )

    with handle_config_incomplete():
        feeder.load()

    feeder.feed()


def feed_works(args):
    """Feed works.

    Args:
        args (argparse.Namespace): Arguments from command line.
    """
    with handle_config_not_found():
        create_logger(wrap=True)
        config = Config(CONFIG_PREFIX)
        config.load_file(directories.user_config_dir / CONFIG_FILE)
        config.check_mandatory_keys(["server"])
        config.set_debug(args.debug)
        set_loglevel(config)

    feeder = WorksFeeder(
        config,
        works_file_path=args.file,
        update_only=args.update_only,
        progress=args.progress,
    )

    with handle_config_incomplete():
        feeder.load()

    feeder.feed()


def feed_tags(args):
    """Feed tags.

    Args:
        args (argparse.Namespace): Arguments from command line.
    """
    with handle_config_not_found():
        create_logger(wrap=True)
        config = Config(CONFIG_PREFIX)
        config.load_file(directories.user_config_dir / CONFIG_FILE)
        config.check_mandatory_keys(["server"])
        config.set_debug(args.debug)
        set_loglevel(config)

    feeder = TagsFeeder(config, tags_file_path=args.file, progress=args.progress)

    with handle_config_incomplete():
        feeder.load()

    feeder.feed()


def feed_work_types(args):
    """Feed work types.

    Args:
        args (argparse.Namespace): Arguments from command line.
    """
    with handle_config_not_found():
        create_logger(wrap=True)
        config = Config(CONFIG_PREFIX)
        config.load_file(directories.user_config_dir / CONFIG_FILE)
        config.check_mandatory_keys(["server"])
        config.set_debug(args.debug)
        set_loglevel(config)

    feeder = WorkTypesFeeder(
        config, work_types_file_path=args.file, progress=args.progress
    )

    with handle_config_incomplete():
        feeder.load()

    feeder.feed()


def main():
    """Main command."""
    parser = get_parser()
    args = parser.parse_args()

    with handle_all_exceptions(
        bugtracker_url="https://github.com/DakaraProject/dakara-feeder/issues",
        logger=logger,
        debug=args.debug,
    ) as exit_value:
        args.function(args)

    sys.exit(exit_value.value)
