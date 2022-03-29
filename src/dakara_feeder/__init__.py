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
    "__date__",
    "__version__",
    "customization",
    "difference",
    "directory",
    "feeder",
    "json",
    "metadata",
    "similarity",
    "song",
    "subtitle",
    "utils",
    "version",
    "web_client",
    "yaml",
]
