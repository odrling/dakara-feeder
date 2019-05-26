from path import Path


class Song:
    def __init__(self, path):
        self.path = Path(path)

    def get_representation(self):
        return {
            "title": self.path.stem,
            "filename": self.path.basename(),
            "directory": self.path.dirname()
        }
