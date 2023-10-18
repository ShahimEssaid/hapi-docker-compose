import logging
from pathlib import Path

import typer

from hapisetup.compose import Compose


class Service:
    def __init__(self, /, *,
                 name: str,
                 path: Path,
                 compose: Compose):
        if not path.absolute().resolve().is_relative_to(compose.path):
            raise ValueError(
                f'Service name: {name} has a path {path} that is not relative to compose path: {compose.path}')
        self.name: str = name
        self.path: Path = path
        self.compose = compose
        self.cli = typer.Typer()

