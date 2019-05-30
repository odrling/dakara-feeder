class Song:
    """Class describing a song

    Args.
        path (path.Path): path to the song file.

    Arguments:
        path (path.Path): path to the song file.
    """

    def __init__(self, path):
        self.path = path

    def get_representation(self):
        """Get the simple representation of the song

        Returns:
            dict: JSON-compiliant structure representing the song.
        """
        return {
            "title": self.path.stem,
            "filename": self.path.basename(),
            "directory": self.path.dirname(),
        }
