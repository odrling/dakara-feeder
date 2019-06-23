class Song:
    """Class describing a song

    Args.
        path (path.Path): path to the song file.

    Attributes:
        path (path.Path): path to the song file.
    """

    def __init__(self, path):
        self.path = path

    def pre_process(self):
        pass

    def post_process(self, representation):
        pass

    def get_duration(self):
        return 0

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
        return ""

    def get_representation(self):
        """Get the simple representation of the song

        Returns:
            dict: JSON-compiliant structure representing the song.
        """
        self.pre_process()
        representation = {
            "title": self.path.stem,
            "filename": self.path.basename(),
            "directory": self.path.dirname(),
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
