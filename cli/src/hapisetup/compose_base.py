import logging
import shutil
import typing
from pathlib import Path

import typer


class ComposeBase:
    def __init__(self, /, *, compose, path: Path, name=None):
        from hapisetup.compose import Compose
        self.compose: Compose = compose
        self.path: Path = path
        self.name: str = name
        self.vars: dict[str, str] = {}
        self.arg_file_list: list[Path] = []
        self.compose_file_list: list[Path] = []
        self.reset_glob_list: list[str] = []
        self.cli: typer.Typer = typer.Typer()

        self._setup_commands()

    def add_compose_file(self, path: typing.Union[str, Path]):
        path = self.compose.get_relative_path(path)
        self._add_item_to_list(path, self.compose_file_list, f'Compose file {path} already added to compose. Ignoring.')

    def add_arg_file(self, path: typing.Union[str, Path]):
        path = self.compose.get_relative_path(path)
        self._add_item_to_list(path, self.arg_file_list, f'Arg file {path} already added to compose. Ignoring.')

    def add_reset_glob(self, glob: str):
        glob = self.get_relative_path(glob)
        self._add_item_to_list(glob, self.reset_glob_list,
                               f'Reset glob {glob} already in reset list {self.reset_glob_list}. Ignoring.')

    def reset_with_globs(self):
        for glob in self.reset_glob_list:
            matches = self.path.glob(str(glob))
            match: Path
            for match in matches:
                if match.is_dir():
                    shutil.rmtree(match)
                elif match.is_file():
                    match.unlink()
                else:
                    raise ValueError(f'Unknown path type: {match}')

    def _add_item_to_list(self, item: typing.Union[str, Path], item_list: list[typing.Union[str, Path]],
                          log_message: str):
        if isinstance(item, Path):
            item = self.compose.get_relative_path(item)
        if item in item_list:
            logging.warning(log_message)
        else:
            item_list.append(item)

    def __str__(self):
        return f'{self.name}@{self.path}'

    def _init_defs(self):

        config_path = self.path / 'config'
        for fragment in self._get_fragments():
            # defs
            paths = self._get_config_files(config_path, f'def{fragment}*.py')
            for path in paths:
                logging.info(f'Loading def file: {path}')
                exec(open(path).read(), self.compose.globals)

    def _init_default_config_files(self):
        config_path = self.path / 'config'
        fragments = self._get_fragments()
        for fragment in fragments:
            paths = self._get_config_files(config_path, f'compose{fragment}*.yaml')
            for path in paths:
                logging.info(f'Using compose file:{path}')
                self.add_compose_file(path)

            paths = self._get_config_files(config_path, f'arg{fragment}*.env')
            for path in paths:
                logging.info(f'Using env file:{path}')
                self.add_arg_file(path)

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
            paths = self._get_config_files(config_path, f'init{fragment}*.py')
            for path in paths:
                logging.info(f'Loading {path}')
                exec(open(path).read(), init_globals)

        if isinstance(self, Service):
            self.compose.services[self.name] = init_globals['service']

        for item in init_globals.items():
            var_name = item[0]
            var_val = item[1]
            if var_name.startswith('CW_'):
                if not isinstance(var_val, str):
                    raise ValueError(f'{self} set var {var_name} to a non string value {var_val}')
                self.vars[var_name] = var_val

    def _get_fragments(self) -> list[str]:
        fragments = []
        fragments.extend(['_default', '_project'])
        fragments.extend([f'_{s}_service' for s in self.compose.service_names])
        fragments.extend([f'_{p}_profile' for p in self.compose.profile_names])
        fragments.append('_local')
        return fragments

    def _get_config_files(self, config_dir: Path, file_patter: str):
        return sorted(list([path for path in config_dir.rglob(file_patter) if path.is_file()]))

    def _setup_commands(self):
        self.cli.command(name='reset')(self.reset_with_globs)

    def get_full_path(self, relative_path: typing.Union[str, Path]) -> Path:
        if isinstance(relative_path, str):
            relative_path = Path(relative_path)
        relative_path.resolve()
        if relative_path.is_absolute():
            if relative_path.is_relative_to(self.path):
                return relative_path
            else:
                raise ValueError(
                    f'Relative path is absolute and outside the compose or service path while getting full path: {relative_path}')
        else:
            return self.path / relative_path

    def get_relative_path(self, other_path: typing.Union[str, Path]) -> Path:
        if isinstance(other_path, str):
            other_path = Path(other_path)
        other_path.resolve()
        if other_path.is_absolute():
            return other_path.relative_to(self.path)
        else:
            return other_path
