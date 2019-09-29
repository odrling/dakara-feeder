#!/usr/bin/env python3
import logging
from argparse import ArgumentParser

from path import Path
from dakara_base.exceptions import DakaraError
from dakara_base.config import load_config, create_logger, set_loglevel

from dakara_feeder.dakara_feeder import DakaraFeeder
from dakara_feeder.config import CONFIG_FILE, create_config


logger = logging.getLogger(__name__)


def get_parser():
    """Get a parser

    Returns:
        argparse.ArgumentParser: parser.
    """
    # main parser
    parser = ArgumentParser(description="Feeder for the Dakara project")

    parser.set_defaults(function=feed)

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="enable debug output, increase verbosity",
    )

    parser.add_argument(
        "-f", "--force", action="store_true", help="force unchanged files to be updated"
    )

    parser.add_argument(
        "--no-progress",
        dest="progress",
        action="store_false",
        help="do not display progress bars",
    )

    parser.add_argument(
        "--config",
        help="path to the config file, default: '{}'".format(CONFIG_FILE),
        default=CONFIG_FILE,
    )

    # subparsers
    subparsers = parser.add_subparsers(title="subcommands")

    # create config subparser
    create_config_subparser = subparsers.add_parser(
        "create-config", help="Create a new config file in current directory"
    )
    create_config_subparser.set_defaults(function=create_config)

    create_config_subparser.add_argument(
        "--force",
        help="overwrite previous config file if it exists",
        action="store_true",
    )

    return parser


def feed(args):
    """Execute the feed action

    Args:
        args (argparse.Namespace): arguments from command line.
    """
    # prepare execution
    create_logger(wrap=True)

    config = load_config(
        Path(args.config), args.debug, mandatory_keys=["kara_folder", "server"]
    )
    set_loglevel(config)

    # do the actual feeding
    feeder = DakaraFeeder(config, force_update=args.force, progress=args.progress)
    feeder.load()
    feeder.feed()


def main():
    parser = get_parser()
    args = parser.parse_args()

    try:
        args.function(args)

    except KeyboardInterrupt:
        logger.info("Quit by user")
        exit(255)

    except SystemExit:
        logger.info("Quit by system")
        exit(254)

    except DakaraError as error:
        if args.debug:
            raise

        logger.critical(error)
        exit(1)

    except BaseException as error:
        if args.debug:
            raise

        logger.exception("Unexpected error: {}".format(error))
        logger.critical(
            "Please fill a bug report at "
            "https://github.com/DakaraProject/dakara-feeder/issues"
        )
        exit(128)

    exit(0)


if __name__ == "__main__":
    main()
