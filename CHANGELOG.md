# Changelog

<!---
## 0.0.1 - 1970-01-01

### Added

- New stuff.

### Changed

- Changed stuff.

### Deprecated

- Deprecated stuff.

### Removed

- Removed stuff.

### Fixed

- Fixed stuff.

### Security

- Security related fix.
-->

## Unreleased

### Added

- Automatically prune artists and works without songs on server.
- Feed tags with command `dakara-feeder feed tags`.
- Feed work types with command `dakara-feeder feed work-types`.
- Feed works with command `dakara-feeder feed works`.

### Changed

- Name of the command changed from `dakara-feed` to `dakara-feeder`.
- Feed command for songs changed from `dakara-feed` to `dakara-feeder feed songs`.
- Custom song can be indicated in config with a file name: `custom_song_class: path/to/file.py::MySong`.

## 1.7.0 - 2021-06-20

### Removed

- Dropped support of Python 3.5 and 3.6.

## 1.6.0 - 2020-09-05

### Added

- Detect instrumental tracks.

## 1.5.1 - 2019-12-06

### Fixed

- A subtitle file from which lyrics can't be parsed no longer halts the feed process but only logs an error.
- A video file from which duration can't be extracted no longer halts the feed process but only logs an error.

## 1.5.0 - 2019-12-05

### Added

- First version.
