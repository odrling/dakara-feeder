from dakara_feeder.metadata_parser import FFProbeMetadataParser
from dakara_feeder.subtitle_parser import Pysubs2SubtitleParser


class Song:
    """Class describing a song

    Args.
        base_directory (path.Path): path to the scanned directory.
        paths (directory_lister.SongPaths): paths of the song file.

    Attributes:
        base_directory (path.Path): path to the scanned directory.
        video_path (path.Path): path to the song file, relative to the base directory.
    """

    def __init__(self, base_directory, paths):
        self.base_directory = base_directory
        self.video_path = paths.video
        self.subtitle_path = paths.subtitle

    def pre_process(self):
        pass

    def post_process(self, representation):
        pass

    def get_duration(self):
        parser = FFProbeMetadataParser.parse(self.base_directory / self.video_path)
        return parser.duration.total_seconds()

    def get_artists(self):
        return []

    def get_works(self):
        return []

    def get_tags(self):
        return []

    def get_version(self):
        return ""

    def get_detail(self):
        return ""

    def get_detail_video(self):
        return ""

    def get_lyrics(self):
        if not self.subtitle_path:
            return ""

        parser = Pysubs2SubtitleParser(self.base_directory / self.subtitle_path)
        return parser.get_lyrics()

    def get_representation(self):
        """Get the simple representation of the song

        Returns:
            dict: JSON-compiliant structure representing the song.
        """
        self.pre_process()
        representation = {
            "title": self.video_path.stem,
            "filename": str(self.video_path.basename()),
            "directory": str(self.video_path.dirname()),
            "duration": self.get_duration(),
            "artists": self.get_artists(),
            "works": self.get_works(),
            "tags": self.get_tags(),
            "version": self.get_version(),
            "detail": self.get_detail(),
            "detail_video": self.get_detail_video(),
            "lyrics": self.get_lyrics(),
        }
        self.post_process(representation)

        return representation
