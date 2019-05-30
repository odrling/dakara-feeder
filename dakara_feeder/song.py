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
        return {
            "title": self.path.stem,
            "filename": self.path.basename(),
            "directory": self.path.dirname(),
        }
