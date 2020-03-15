from dakara_feeder import TagsFeeder
from dakara_feeder.commands.base import Subcommand


class TagsSubcommand(Subcommand):
    name = "tags"
    description = "Feed tags to the server"

    def set_subparser(self, subparser):
        subparser.add_argument(
            "file", help="path to the tags configuration file",
        )

    def handle(self, args):
        config = self.load_config(args.debug)
        feeder = TagsFeeder(config, tags_file_path=args.file, progress=args.progress)
        self.load_feeder(feeder)

        # do the actual feeding
        feeder.feed()
