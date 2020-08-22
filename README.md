# Dakara Feeder

[![Travis CI Build Status](https://travis-ci.com/DakaraProject/dakara-feeder.svg?branch=develop)](https://travis-ci.com/DakaraProject/dakara-feeder)
[![Appveyor CI Build status](https://ci.appveyor.com/api/projects/status/7vxx2dyu8y25v6of?svg=true)](https://ci.appveyor.com/project/neraste/dakara-feeder/branch/develop)
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

* Python3, to make everything up and running (supported versions: 3.5, 3.6, 3.7 and 3.8);
* [ffmpeg](https://www.ffmpeg.org/), to extract lyrics and extract metadata from files (preferred way);
* [MediaInfo](https://mediaarea.net/fr/MediaInfo/), to extract metadata from files (slower, alternative way, may not work on Windows).

Linux and Windows are supported.

### Virtual environment

It is strongly recommended to use the Dakara feeder within a virtual environment.

### Install

Install the package with:

```sh
pip install dakarafeeder
```

If you have downloaded the repo, you can install the package directly with:

```sh
python setup.py install
```

## Usage

### Commands

The package provides the `dakara-feed` command which will find songs in the configured directory, parse them and send their data to a running instance of the Dakara server:

```sh
dakara-feed
# or
python -m dakara_feed
```

One instance of the Dakara server should be running.
For more help:

```sh
dakara-feed -h
# or
python -m dakara_feed -h
```

Before calling the function, you should create a config file with:

```sh
dakara-feed create-config
# or
python -m dakara_feed create-config
```

and complete it with your values. The file is stored in your user space: `~/.config/dakara` on Linux or `$APPDATA\Dakara` on Windows.

The data extracted from songs are very limited in this package by default, as data can be stored in various ways in song files. You are encouraged to make your own parser, see next subsection.

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

The file must be in the same directory you are calling `dakara-feed`, or in any directory reachable by Python.
To register your customized `Song` class, you simply enable it in the config file:

```yaml
# Custom song class to use
# If you want to extract additional data when parsing files (video, subtitle or
# other), you can write your own Song class, derived from
# `dakara_feeder.song.BaseSong`. See documentation of BaseSong for more details
# on how to proceed.
# Indicate the module name of the class to use.
# Default is BaseSong, which is pretty basic.
custom_song_class: my_song.Song
```

Now, `dakara-feed` will use your customized `Song` class instead of the default one.

## Developpment

### Install dependencies

Please ensure you have a recent enough version of `setuptools`:

```sh
pip install --upgrade "setuptools>=40.0"
```

Install the dependencies with:

```sh
pip install -e ".[tests]"
```

This installs the normal dependencies of the package plus the dependencies for tests.

### Run tests

Run tests simply with:

```sh
python setup.py test
```

To check coverage, use the `coverage` command:

```sh
coverage run setup.py test
coverage report -m
```

### Hooks

Git hooks are included in the `hooks` directory.

Use the following command to use this hook folder for the project:

```
git config core.hooksPath hooks
```

If you're using git < 2.9 you can make a symlink instead:

```
ln -s -f ../../hooks/pre-commit .git/hooks/pre-commit
```

### Code style

The code follows the [PEP8](https://www.python.org/dev/peps/pep-0008/) style guide (88 chars per line).
Quality of code is checked with [Flake8](https://pypi.org/project/flake8/).
Style is enforced using [Black](https://github.com/ambv/black).
You need to call Black before committing changes.
You may want to configure your editor to call it automatically.
Additionnal checking can be manually performed with [Pylint](https://www.pylint.org/).
