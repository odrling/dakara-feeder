#!/usr/bin/env python3
from argparse import ArgumentParser

from dakara_feeder.dakara_feeder import DakaraFeeder


CONFIG_FILE_PATH = "config.yaml"


def get_parser():
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
    feeder = DakaraFeeder(args.config, args.debug)
    feeder.feed()


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
