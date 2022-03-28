"""
Dakara feeder.

Feed the database of the Dakara server.
"""

from dakara_feeder import (
    customization,
    difference,
    directory,
    feeder,
    json,
    metadata,
    similarity,
    song,
    subtitle,
    utils,
    version,
    web_client,
    yaml,
)
from dakara_feeder.version import __date__, __version__

__all__ = [
    "customization",
    "directory",
    "similarity",
    "subtitle",
    "version",
    "yaml",
    "difference",
    "json",
    "metadata",
    "song",
    "utils",
    "feeder",
    "web_client",
    "__version__",
    "__date__",
]
