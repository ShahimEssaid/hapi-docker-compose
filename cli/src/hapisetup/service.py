from pathlib import Path

from hapisetup.compose import Compose
from hapisetup.compose_base import ComposeBase


class Service(ComposeBase):
    def __init__(self, /, *,
                 name: str,
                 path: Path,
                 compose: Compose):
        super().__init__(compose=compose, path=path, name=name)
        relative_path = str(compose.get_relative_path(self.path))
        self.env_vars[f'CW_{self.name.upper()}_HOME'] = str(compose.get_relative_path(self.path))

        if not path.absolute().resolve().is_relative_to(compose.path):
            raise ValueError(
                f'Service name: {name} has a path {path} that is not relative to compose path: {compose.path}')
