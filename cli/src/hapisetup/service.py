import logging
from pathlib import Path

import typer

from hapisetup.compose import Compose
from hapisetup.compose_base import ComposeBase


class Service(ComposeBase):
    def __init__(self, /, *,
                 name: str,
                 path: Path,
                 compose: Compose):
        super().__init__(compose=compose, path=path, name=name)

        self.init()
        if not path.absolute().resolve().is_relative_to(compose.path):
            raise ValueError(
                f'Service name: {name} has a path {path} that is not relative to compose path: {compose.path}')
