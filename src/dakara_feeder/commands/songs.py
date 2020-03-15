from dakara_feeder import SongsFeeder
from dakara_feeder.commands.base import Subcommand


class SongsSubcommand(Subcommand):
    name = "songs"
    description = "Feed songs to the server"

    def set_subparser(self, subparser):
        subparser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="force unchanged files to be updated",
        )

        subparser.add_argument(
            "--no-prune",
            dest="prune",
            action="store_false",
            help="do not delete artists and works without songs at end of feed",
        )

    def handle(self, args):
        config = self.load_config(args.debug)
        feeder = SongsFeeder(
            config, force_update=args.force, prune=args.prune, progress=args.progress
        )
        self.load_feeder(feeder)

        # do the actual feeding
        feeder.feed()
