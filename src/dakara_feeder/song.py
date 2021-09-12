import logging

from dakara_feeder.metadata_parser import (
    FFProbeMetadataParser,
    MediaParseError,
    NullMetadataParser,
)
from dakara_feeder.subtitle_parser import Pysubs2SubtitleParser, SubtitleParseError


logger = logging.getLogger(__name__)


class BaseSong:
    """Class describing a song

    This class is supposed to be overloaded for getting more data from song
    files.

    The main entry point of the class when used by the feeder is the
    `get_representation` method, that will call all the methods to get the song
    data:
        - `get_title`;
        - `get_duration`;
        - `get_has_instrumental`;
        - `get_version`;
        - `get_detail`;
        - `get_detail_video`;
        - `get_tags`;
        - `get_artists`;
        - `get_works`;
        - `get_lyrics`.

    You should override those methods to suit your needs. See the documentation
    of each method to learn what data format the must return.

    When calling `get_representation`, two special methods are also called for
    performing custom actions, the first one just on entering
    `get_representation`, and the other just befor leaving it:
        - `pre_process`;
        - `post_process`.

    You should override those two methods as well. Typically, `pre_process`
    should be overriden to perform preparative actions which result would be
    used by the `get_` methods. On the other hand, `post_process` should be
    overriden to perform final actions on the representation.

    Metadata of the video file are extracted using a metadata parser and stored
    in the `metadata` attribute. The metadata parser to chose is decided by
    setting the class attribute `metadata_parser_class`. The class must
    implement `dakara_feeder.metadata_parser.MetadataParser` base class. So far,
    two implemenations are available in the project:
        - `dakara_feeder.metadata_parser.FFProbeMetadataParser`, based on
            FFProbe, part of FFMpeg (external dependency). This is the recommended
            and the default parser;
        - `dakara_feeder.metadata_parser.MediainfoMetadataParser`, based on
            MediaInfo (external dependency). Slower, may not work on Windows.

    Metadata are available when calling `pre_process`.

    If the metadata cannot be extracted from the video file for any reason, the
    `metadata` attribute will contain a
    `dakara_feeder.metadata_parser.NullMetadataParser` that always return null
    values (e.g. 0 seconds duration).

    Args.
        base_directory (path.Path): path to the scanned directory.
        paths (directory_lister.SongPaths): paths of the song file.

    Attributes:
        metadata_parser_class (type): Class of the metadata parser to use.
            Default to `dakara_feeder.metadata_parser.FFProbeMetadataParser`.
        base_directory (path.Path): path to the scanned directory.
        video_path (path.Path): path to the song file, relative to the base
            directory.
        audio_path (path.Path): path to the audio file, relative to the base
            directory.
        sublitle_path (path.Path): path to the subtitle file, relative to the
            base directory.
        others_path (list of path.Path): list of paths to the other files,
            relative to the base directory.
        metadata (dakara_feeder.metadata_parser.MetadataParser): Object for
            containing metadata of the video file.
    """

    metadata_parser_class = FFProbeMetadataParser

    def __init__(self, base_directory, paths):
        self.base_directory = base_directory
        self.video_path = paths.video
        self.audio_path = paths.audio
        self.subtitle_path = paths.subtitle
        self.others_path = paths.others
        self.metadata = NullMetadataParser.parse(self.video_path)

    def parse_metadata(self):
        """Use the requested metadata parser to parse video file
        """
        try:
            self.metadata = self.metadata_parser_class.parse(
                self.base_directory / self.video_path
            )

        except MediaParseError as error:
            logger.error("Cannot parse metadata: {}".format(error))

    def pre_process(self):
        """Process preparative actions

        This method should be overriden. By default, it does not do anything.

        This method is called at the beginning of `get_representation` and can
        be used to cache data in the instance.
        """
        pass

    def post_process(self, representation):
        """Process final actions

        This method should be overriden. By default, it does not do anything.

        This method is called at the end of `get_representation` and can be
        used to modify the representation.

        Args:
            representation (dict): JSON-compiliant structure representing the
            song.
        """
        pass

    def get_title(self):
        """Get the title

        This method should be overriden. By default it returns the video file
        name without extension.

        Returns:
            str: Title of the song.
        """
        return self.video_path.stem

    def get_duration(self):
        """Get the duration

        This method may be overriden. By default it returns the duration of the
        video file using FFProbe.


        Returns:
            float: Duration of the song in seconds.
        """
        return self.metadata.get_duration().total_seconds()

    def get_has_instrumental(self):
        """Get the flag if the song has an instrumental track

        Returns:
            bool: True either if there is an extra audio file siding with the
            video file, or if the video file has more than 2 audio tracks.
        """
        if self.audio_path:
            return True

        if self.metadata.get_audio_tracks_count() >= 2:
            return True

        return False

    def get_artists(self):
        """Get the list of artists

        This method should be overriden. By default it returns an empty list.

        Returns:
            list of dict: List of representations of artists. An artist is a
            dictionary containing only one key:
                - name (str): The name of the artist.
        """
        return []

    def get_works(self):
        """Get the list of work links

        This method should be overriden. By default it returns an empty list.

        Returns:
            list of dict: List of representations of work links. A work link is
            a dictionary containing the following keys:
                - link_type (str): Type of link between the song and the work.
                    Can be either:
                        - "OP", for opening;
                        - "ED", for ending;
                        - "IN", for insert song;
                        - "IS", for image song.
                    You should read the server documentation about those terms;
                - link_type_number (int): For link_type "OP" or "ED", add an
                    ordinal value (e.g. in OP1, OP2);
                - episodes (str): List of episodes where the song is used in
                    the work (e.g. "1, 2, 5");
                - work (dict): Representation of a work, containing the
                    following keys:
                        - title (str): Title of the work;
                        - subtitle (str): Subtitle of the work;
                        - work_type (dict): Representation of the type of a
                            work (e.g. anime), containing the following keys:
                                - query_name (str): Technical name of the type.
                                    To use an existing work type, you should
                                    use only this key;
                                - name (str): Name of the type (not mandatory);
                                - name_plural (str): Plural name of the type
                                    (not mandatory);
                                - icon_name (str): Name of the icon that
                                    represents this work type visually (not
                                    mandatory);
                        - alternative_titles (list of dict): List of
                            representations of alternative titles. An
                            alternative title is a dictionary containing only
                            one key:
                                - title (str): Alternative title of the work.
        """
        return []

    def get_tags(self):
        """Get the list of tags

        This method should be overriden. By default it returns an empty list.

        Returns:
            list of dict: List of representations of tags. A tag is a ditionary
            containing the following keys:
                - name (str): Name of the tag;
                - color_hue (int): Visual hue of the tag (not mandatory);
                - disabled (bool): True if the tag is disabled (not mandatory).
        """
        return []

    def get_version(self):
        """Get the version

        This method should be overriden. By default it returns an empty string.

        Returns:
            str: Version of the song.
        """
        return ""

    def get_detail(self):
        """Get the datail

        This method should be overriden. By default it returns an empty string.

        Returns:
            str: Detail about the song.
        """
        return ""

    def get_detail_video(self):
        """Get the datail of the video

        This method should be overriden. By default it returns an empty string.

        Returns:
            str: Detail about the video.
        """
        return ""

    def get_lyrics(self):
        """Get the lyrics

        This method may be overriden. By default it returns a string containing
        the lyrics of the song extracted from the subtitle file using Pysubs2.
        If there is no subtitle file, it returns an empty string.

        Lyrics can be extracted from the subtitle file using a parser. One
        parser is available in the project:
            - `dakara_feeder.subtitle_parser.Pysubs2SubtitleParser`, based on
                Pysubs2.

        Returns:
            str: Lyrics on the song.
        """
        if not self.subtitle_path:
            return ""

        try:
            parser = Pysubs2SubtitleParser.parse(
                self.base_directory / self.subtitle_path
            )
            return parser.get_lyrics()
        except SubtitleParseError as error:
            logger.error("Lyrics not parsed: {}".format(error))
            return ""

    def get_representation(self):
        """Get the simple representation of the song

        Returns:
            dict: JSON-compiliant structure representing the song.
        """
        self.parse_metadata()
        self.pre_process()
        representation = {
            "title": self.get_title(),
            "filename": str(self.video_path.basename()),
            "directory": str(self.video_path.dirname()),
            "duration": self.get_duration(),
            "has_instrumental": self.get_has_instrumental(),
            "version": self.get_version(),
            "detail": self.get_detail(),
            "detail_video": self.get_detail_video(),
            "tags": self.get_tags(),
            "artists": self.get_artists(),
            "works": self.get_works(),
            "lyrics": self.get_lyrics(),
        }
        self.post_process(representation)

        return representation
