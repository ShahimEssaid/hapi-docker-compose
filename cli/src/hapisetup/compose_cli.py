import logging
import os
import pathlib
import sys
import typing
from pathlib import Path
import time

import typer
from typing_extensions import Annotated

from hapisetup.compose import Compose

dc_home = os.environ.get('DC_HOME', str(Path.cwd()))
dc_home_path = Path(dc_home).absolute().resolve()

timestr = time.strftime("%Y%m%d-%H%M%S")


for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename=dc_home_path / 'logs' / f'{timestr}.log', encoding='utf-8', level=logging.INFO,
                    filemode='w')

compose = Compose(compose_path=dc_home_path)
compose.init()
