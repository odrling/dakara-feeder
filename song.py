from dakara_feeder.song import BaseSong


class WonderSong:
    class TheRealSong(BaseSong):
        def get_title(self):
            return self.video_path.stem.split(" - ")[2]

        def get_artists(self):
            return [{"name": self.video_path.stem.split(" - ")[0]}]

        def get_duration(self):
            return 0
