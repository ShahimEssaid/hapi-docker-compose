import logging
import os
import pathlib
import sys
import typing
from pathlib import Path

import typer
from typing_extensions import Annotated

from hapisetup.compose import Compose

dc_home = os.environ.get('DC_HOME', str(Path.cwd()))
dc_home_path = Path(dc_home).absolute().resolve()

compose = Compose(compose_path=dc_home_path)
compose.init()
