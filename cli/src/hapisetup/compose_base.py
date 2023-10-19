import logging
import typing
from pathlib import Path

import typer


class ComposeBase:
    def __init__(self, /, *, compose, path: Path, name=None):
        from hapisetup.compose import Compose
        self.compose: Compose = compose
        self.path: Path = path
        self.name = name
        self.env_vars: dict[str, str] = {}
        self.env_files: list[Path] = []
        self.compose_files: list[Path] = []
        self.cli: typer.Typer = typer.Typer()

    def add_compose_file(self, compose_file_path: typing.Union[str, Path]):
        compose_file_path = self.compose.get_relative_path(compose_file_path)
        if compose_file_path in self.compose_files:
            logging.warning(f'Compose file {compose_file_path} already added to compose. Ignoring.')
        else:
            self.compose_files.append(compose_file_path)

    def add_compose_env_file(self, compose_env_file_path: typing.Union[str, Path]):
        compose_env_file_path = self.compose.get_relative_path(compose_env_file_path)
        if compose_env_file_path in self.compose_files:
            logging.warning(f'Compose env file {compose_env_file_path} already added to compose. Ignoring.')
        else:
            self.env_files.append(compose_env_file_path)

    def __str__(self):
        return f'{self.name}@{self.path}'

    def _init_defs(self):
        fragments = []
        fragments.extend(['', '_project'])
        fragments.extend([f'_{s}_service' for s in self.compose.service_names])
        fragments.extend([f'_{p}_profile' for p in self.compose.profile_names])
        config_path = self.path / 'config'
        for fragment in self._get_fragments():
            # defs
            def_file = config_path / f'init_defs{fragment}.py'
            if def_file.exists():
                logging.info(f'Loading def file: {def_file}')
                exec(open(def_file).read(), self.compose.globals)

    def _init_default_config_files(self):
        config_path = self.path / 'config'
        fragments = self._get_fragments()
        for fragment in fragments:
            compose_file = config_path / f'compose{fragment}.yaml'
            if compose_file.exists():
                self.add_compose_file(compose_file)

            env_file = config_path / f'compose{fragment}.env'
            if env_file.exists():
                self.add_compose_env_file(env_file)

    def _init_scripts(self):

        # do defs.  No service instance set in globals
        # The Compose defs run, and then the Services ones later as they're instantiated. This should work given that
        # Service defs should not overwrite Compose defs
        # All defs get added to the compose.globals

        # init scripts
        init_globals = dict(self.compose.globals)
        from hapisetup.service import Service
        if isinstance(self, Service):
            init_globals['service'] = self

        config_path = self.path / 'config'
        for fragment in self._get_fragments():
            init_path = config_path / f'init{fragment}.py'
            if init_path.exists():
                logging.info(f'Loading {init_path}')
                exec(open(init_path).read(), init_globals)

        if isinstance(self, Service):
            self.compose.services[self.name] = init_globals['service']

        for item in init_globals.items():
            var_name = item[0]
            var_val = item[1]
            if var_name.startswith('CW_'):
                if not isinstance(var_val, str):
                    raise ValueError(f'{self} set var {var_name} to a non string value {var_val}')
                self.env_vars[var_name] = var_val

    def _get_fragments(self) -> list[str]:
        fragments = []
        fragments.extend(['', '_project'])
        fragments.extend([f'_{s}_service' for s in self.compose.service_names])
        fragments.extend([f'_{p}_profile' for p in self.compose.profile_names])
        fragments.append('_local')
        return fragments
