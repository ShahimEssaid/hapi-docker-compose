from os import environ
from pathlib import Path

# Set this to a path to a Maven source folder to build the HAPI binary from
# This is mostly useful for development purposes. Others would point to the repo
# for this source. This setting overrides the configured repo.
environ['HS_HAPI_BUILD_SOURCE_PATH'] = \
    str(Path('/some/path/to/hapi/source'))

