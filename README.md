# Dakara Feeder

<!-- Badges are displayed for the develop branch -->
[![Appveyor CI Build status](https://ci.appveyor.com/api/projects/status/8qpr1lk1kye7fkf0/branch/develop?svg=true)](https://ci.appveyor.com/project/neraste/dakara-feeder/branch/develop)
[![Codecov coverage analysis](https://codecov.io/gh/DakaraProject/dakara-feeder/branch/develop/graph/badge.svg)](https://codecov.io/gh/DakaraProject/dakara-feeder)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PyPI version](https://badge.fury.io/py/dakarafeeder.svg)](https://pypi.python.org/pypi/dakarafeeder/)
[![PyPI Python versions](https://img.shields.io/pypi/pyversions/dakarafeeder.svg)](https://pypi.python.org/pypi/dakarafeeder/)

Allows to feed the database of the Dakara server remotely.

## Installation

This repo is tied with the Dakara server, so you should setup it first:

* [Dakara server](https://github.com/DakaraProject/dakara-server/).

Other important parts of the project include:

* [Dakara VLC player](https://github.com/DakaraProject/dakara-player-vlc/).

### System requirements

* Python3, to make everything up and running (supported versions: 3.7, 3.8, 3.9, 3.10 and 3.11);
* [ffmpeg](https://www.ffmpeg.org/), to extract lyrics and extract metadata from files (preferred way);
* [MediaInfo](https://mediaarea.net/fr/MediaInfo/), to extract metadata from files (slower, alternative way, may not work on Windows).

Linux and Windows are supported.

### Virtual environment

It is strongly recommended to use the Dakara feeder within a virtual environment.

### Install

Please ensure you have a recent enough version of `setuptools`:

```sh
pip install --upgrade "setuptools>=46.4.0"
```

Install the package with:

```sh
pip install dakarafeeder
```

If you have downloaded the repo, you can install the package directly with:

```sh
pip install .
```

## Usage

### Commands

The package provides the `dakara-feeder feed` command for creating data on a running instance of the Dakara server.
Several sub-commands are available.
To begin, `dakara-feeder feed songs` will find songs in the configured directory, parse them and send their data:

```sh
dakara-feeder feed songs
# or
python -m dakara_feeder feed songs
```

One instance of the Dakara server should be running.

The data extracted from songs are very limited in this package by default, as data can be stored in various ways. You are encouraged to make your own parser (see [this section](#making-a-custom-parser) for more details).

Then, `dakara-feeder feed tags` and `dakara-feeder feed work-types` will find tags and work types in a YAML file (see [this section](#tags-and-work-types-file) for more details):

```sh
dakara-feeder feed tags path/to/tags.yaml
# or
python -m dakara_feeder feed tags path/to/tags.yaml
```

and:

```sh
dakara-feeder feed work-types path/to/work_types.yaml
# or
python -m dakara_feeder feed work-types path/to/work_types.yaml
```

Also, `dakara-feeder feed works` will find works in a JSON file (see [this section](#works-file) for more details):

```sh
dakara-feeder feed works path/to/works.json
# or
python -m dakara_feeder feed works path/to/works.json
```

For more help:

```sh
dakara-feeder -h
# or
python -m dakara_feeder -h
```

Before calling any command, you should create a config file with:

```sh
dakara-feeder create-config
# or
python -m dakara_feeder create-config
```

and complete it with your values. The file is stored in your user space: `~/.config/dakara` on Linux, or `$APPDATA\DakaraProject\dakara` on Windows.

### Configuration

The configuration is created with the previously cited command. Several aspect of the feeder can be configured with this file. Please check with the file documentation.

Authentication to the server can be done with username and password, or with a token that can be copied from the web client. Please note that only a library manager can use the feeder.

### Making a custom parser

To override the extraction of data from song files, you should create a class derived from `dakara_feeder.song.BaseSong`. Please refer to the documentation of this class to learn which methods to override, and what attributes and helpers are at your disposal.

Here is a basic example. It considers that the song video file is formatted in the way "title - main artist.ext":

```python
# my_song.py
from dakara_feeder.song import BaseSong

class Song(BaseSong):
    def get_title(self):
        return self.video_path.stem.split(" - ")[0]

    def get_artists(self):
        return [{"name": self.video_path.stem.split(" - ")[1]}]
```

To register your customized `Song` class, you simply indicate it in the configuration file.
You can either indicate an importable module or a file:

```yaml
custom_song_class: path/to/my_song.py::Song
# or
custom_song_class: my_song.Song
```

Now, `dakara-feeder` will use your customized `Song` class instead of the default one.

### Tags and work types file

Whilst data from songs are extracted directly from song files, data from tags and work types are extracted from a YAML file.
All data can coexist in the same file.

#### Tags

Tags will be searched in the key `tags`.
Tags are identified by their name (it will be displayed in upper case, it
should be just one word).
You can provide a color hue (positive integer from 0 to 360):

```yaml
tags:
  - name: PV
    color_hue: 162
  - name: AMV
    color_hue: 140
```

#### Work types

Work types will be searched in the key `worktypes`
Work types are identified by their query name (hyphenated name, with no special
characters, used as keyword for querying).
You can provide a work type display name (singular and plural) and an icon name (choosen among the
[FontAwesome](http://fontawesome.io/icons/) font glyphes):

```yaml
worktypes:
  - query_name: anime
    name: Anime
    name_plural: Animes
    icon_name: television
  - query_name: live-action
    name: Live action
    name_plural: Live actions
    icon_name: film
```

### Works file

You can provide more information about works (especially alternative names) from a JSON file.
The file should contain a dictionary where keys are work types query name and values lists of works representation:

```json
{
  "work_type_1":
    [
      {
        "title": "Work 1",
        "subtitle": "Subtitle 1",
        "alternative_titles": [
          {
            "title": "AltTitle 1"
          },
          {
            "title": "AltTitle 2"
          }
        ]
      },
      {
        "title": "Work 2",
        "subtitle": "Subtitle 2"
      }
    ],
  "work_type_2": []
}
```

Identification with existing works on the server is made with the work type, the title and the subtitle, case insensitively.

## Development

Please read the [developers documentation](CONTRIBUTING.md).
