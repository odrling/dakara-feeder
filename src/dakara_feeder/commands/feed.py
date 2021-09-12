"""Entry point for the dakara-feed command."""

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

from dakara_feeder import SongsFeeder, commands
from dakara_feeder.commands.base import CONFIG_FILE, Subcommand
from dakara_feeder.version import __date__, __version__

logger = logging.getLogger(__name__)


def get_subcommands():
    """Get subcommand classes

    The subcommands must be listed in `dakara_feeder.commands.__init__`.

    Returns:
        list: list of subcommand classes.
    """
    subcommands = []
    for item_name in sorted(commands.__all__):
        item = getattr(commands, item_name)
        if issubclass(item, Subcommand):
            subcommands.append(item)

    return subcommands


def get_parser():
    """Get the parser.

    Returns:
        argparse.ArgumentParser: Parser.
    """
    # main parser
    parser = ArgumentParser(
        prog="dakara-feed", description="Feeder for the Dakara project"
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="enable debug output, increase verbosity",
    )

    parser.add_argument(
        "--no-progress",
        dest="progress",
        action="store_false",
        help="do not display progress bars",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {} ({})".format(__version__, __date__),
    )

    # subparsers
    subparsers = parser.add_subparsers(title="subcommands")

    # add the subparser of each subcommand
    for subcommand in get_subcommands():
        subcommand().create_subparser(subparsers)

    # if no subcommand is requested, print help
    parser.set_defaults(function=lambda args: parser.print_help())

    return parser


def feed(args):
    """Execute the feed action.

    Args:
        args (argparse.Namespace): Arguments from command line.
    """
    create_logger(wrap=True)

    # load the config, display help to create config if it fails
    try:
        config = load_config(
            get_config_file(CONFIG_FILE),
            args.debug,
            mandatory_keys=["kara_folder", "server"],
        )

    except ConfigNotFoundError as error:
        raise ConfigNotFoundError(
            "{}, please run 'dakara-feed create-config'".format(error)
        ) from error

    set_loglevel(config)
    feeder = SongsFeeder(config, force_update=args.force, progress=args.progress)

    # load the feeder, consider that the config is incomplete if it fails
    try:
        feeder.load()

    except DakaraError:
        logger.warning(
            "Config may be incomplete, please check '{}'".format(
                get_config_file(CONFIG_FILE)
            )
        )
        raise

    # do the actual feeding
    feeder.feed()


def create_config(args):
    """Create the config.

    Args:
        args (argparse.Namespace): Arguments from command line.
    """
    create_logger(custom_log_format="%(message)s", custom_log_level="INFO")
    create_config_file("dakara_feeder.resources", CONFIG_FILE, args.force)
    logger.info("Please edit this file")


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
