import logging
import typing
from os import environ
from pathlib import Path
from subprocess import Popen

import typer
from typing_extensions import Annotated

from hapisetup.compose_base import ComposeBase


class Compose(ComposeBase):
    def __init__(self, /, *,
                 compose_path: Path,
                 ):
        super().__init__(compose=self, path=compose_path.absolute().resolve())

        self.service_names: list[str] = []
        self.profile_names: list[str] = []

        self.cli.command(name='compose',
                         context_settings=dict(
                             ignore_unknown_options=True,
                             allow_extra_args=True),
                         add_help_option=False)(self._run_compose)

        from hapisetup.service import Service
        self.services: dict[str, Service] = {}
        self.globals = {'compose': self,
                        'Compose': Compose,
                        'Service': Service}

    def get_all_compose_files(self) -> list[Path]:
        files = list(self.compose_files)
        for s in self.services.values():
            files.extend(s.compose_files)
        return files

    def get_all_env_files(self) -> list[Path]:
        files = list(self.env_files)
        for s in self.services.values():
            files.extend(s.env_files)
        return files

    def get_effective_env_vars(self) -> dict[str, str]:

        env_vars = dict()
        env_vars.update(self.env_vars)
        for service in self.services.values():
            env_vars.update(service.env_vars)
        # environment overrides
        env_vars.update(environ)
        key_list = list(env_vars.keys())
        key_list.sort()
        sorted_vars = {k: env_vars[k] for k in key_list}
        # for item in sorted_vars.items():
        #     print(f'{item[0]}  -->  {item[1]}')
        return sorted_vars

    def _run_compose(self, ctx: Annotated[typer.Context, typer.Argument()]):
        compose_line = ['docker', 'compose', '--project-directory', self.path]
        kwargs = {'stdout': None, 'stderr': None}
        for f in self.get_all_compose_files():
            compose_line.append('-f')
            compose_line.append(f)

        env_files = self.get_all_env_files()
        for f in env_files:
            compose_line.append('--env-file')
            compose_line.append(f)

        cli_args = ctx.args
        compose_line.extend(cli_args)
        logging.info(f'compose: {compose_line}')
        popen = Popen(compose_line, env=self.get_effective_env_vars(), **kwargs)
        popen.wait()
        return popen

    def get_full_path(self, relative_path: typing.Union[str, Path]) -> Path:
        if isinstance(relative_path, str):
            relative_path = Path(relative_path)
        relative_path.resolve()
        if relative_path.is_absolute():
            if relative_path.is_relative_to(self.path):
                return relative_path
            else:
                raise ValueError(
                    f'Relative path is absolute and outside compose while getting full path: {relative_path}')
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

    def hi(self, message: str):
        print(f' =========== hello {self} {message}')

    def init(self):
        # First run
        # discover service and profile names and populate those lists. These should not change with the second path
        # see if we have them in the effective environment

        # load the defs
        super()._init_defs()
        super()._init_scripts()

        # we should have service and profile names by this point
        services_string = self.get_effective_env_vars().get('CW_SERVICES', None)
        profiles_string = self.get_effective_env_vars().get('CW_PROFILES', None)
        if services_string is None or profiles_string is None:
            raise ValueError(f'Unable to find services string: {services_string} or profiles string: {profiles_string}')

        # collect profile names
        for profile in [p.strip() for p in profiles_string.split(',') if p.strip()]:
            if profile in self.profile_names:
                logging.warning(
                    f'Duplicate profile name: {profile} in profiles: {self.profile_names}. Ignoring.')
            else:
                self.profile_names.append(profile)
        # collect service names and services
        for service_entry in [e.strip() for e in services_string.split(',') if e.strip()]:
            service_parts = service_entry.split(':')
            service_name = service_parts[0].strip()
            service_dirname = service_parts[1].strip()

            if service_name in self.service_names:
                logging.warning(
                    f'Duplicate service name: {service_name} with service path: {service_dirname} in service names: {self.service_names}  while initializing. Ignoring')
            else:
                self.service_names.append(service_name)
                if service_dirname:
                    from hapisetup.service import Service
                    service = Service(name=service_name,
                                      path=self.get_full_path(service_dirname),
                                      compose=self)
                    self.services[service_name] = service

        # now that we have service and profile names we can do the full initialization

        # init defs and load files first
        self._init_defs()
        self._init_default_config_files()

        for service in self.services.values():
            service._init_defs()
            service._init_default_config_files()

        self._init_scripts()
        for service in self.services.values():
            service._init_scripts()

        for service in self.services.values():
            self.cli.add_typer(service.cli, name=service.name)

        hello_typer = typer.Typer(rich_markup_mode="markdown")

        hello_typer.command(name='hi')(self.hi)

        self.cli.add_typer(hello_typer, name='hello')
