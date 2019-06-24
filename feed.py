#!/usr/bin/env python3
import logging
from argparse import ArgumentParser

from path import Path

from dakara_feeder.dakara_feeder import DakaraFeeder
from dakara_feeder.exceptions import DakaraFeederError


CONFIG_FILE_PATH = "config.yaml"


logger = logging.getLogger(__name__)


def get_parser():
    """Get a parser

    Returns:
        argparse.ArgumentParser: parser.
    """
    parser = ArgumentParser(description="Feeder for the Dakara project")

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="enable debug output, increase verbosity",
    )

    parser.add_argument(
        "--config",
        help="path to the config file, default: '{}'".format(CONFIG_FILE_PATH),
        default=CONFIG_FILE_PATH,
    )

    return parser


def feed(args):
    """Execute the feed action
    """
    feeder = DakaraFeeder(Path(args.config), args.debug)
    feeder.configure_logger()
    feeder.feed()


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    try:
        feed(args)

    except DakaraFeederError as error:
        logger.critical(error)
        exit(1)

    except BaseException as error:
        logger.exception("Unexpected error: {}".format(error))
        logger.critical(
            "Please fill a bug report at "
            "https://github.com/DakaraProject/dakara-feeder/issues"
        )
        exit(255)

    exit(0)
