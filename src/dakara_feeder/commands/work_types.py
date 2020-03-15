from dakara_feeder import WorkTypesFeeder
from dakara_feeder.commands.base import Subcommand


class WorkTypesSubcommand(Subcommand):
    name = "work-types"
    description = "Feed work types to the server"

    def set_subparser(self, subparser):
        subparser.add_argument(
            "file", help="path to the work types configuration file",
        )

    def handle(self, args):
        config = self.load_config(args.debug)
        feeder = WorkTypesFeeder(
            config, work_types_file_path=args.file, progress=args.progress
        )
        self.load_feeder(feeder)

        # do the actual feeding
        feeder.feed()
