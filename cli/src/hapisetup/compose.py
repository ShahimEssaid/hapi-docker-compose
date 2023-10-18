import subprocess
import typing
from functools import partial, update_wrapper
from os import environ
from pathlib import Path
import logging
from subprocess import Popen

import typer
from typing_extensions import Annotated

from hapisetup.compose_base import ComposeBase


class Compose(ComposeBase):
    def __init__(self, /, *,
                 compose_path: Path,
                 ):
        super().__init__(compose=self, path=compose_path.absolute().resolve())

        self.profiles: list[str] = []

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

    def get_all_env_vars(self) -> dict[str, str]:

        env_vars = dict()
        env_vars.update(self.env_vars)
        for s in self.services.values():
            env_vars.update(s.env_vars)
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

        for f in self.get_all_env_files():
            compose_line.append('--env-file')
            compose_line.append(f)

        cli_args = ctx.args
        compose_line.extend(cli_args)
        logging.info(f'compose: {compose_line}')
        popen = Popen(compose_line, env=self.get_all_env_vars(), **kwargs)
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
        super().init()

        # # # load compose defs, if any
        # # for fragment in ['', '_project', '_local']:
        # #     defs_path = self.path / 'config' / f'init{fragment}_defs.py'
        # #     if defs_path.exists():
        # #         logging.info(f'Loading {defs_path}')
        # #         exec(open(defs_path).read(), self.globals)
        #
        # # load compose inits, if any
        # init_globals = dict(self.globals)
        # for fragment in ['', '_project', '_local']:
        #     init_path = self.path / 'config' / f'init{fragment}.py'
        #     if init_path.exists():
        #         logging.info(f'Loading {init_path}')
        #         exec(open(init_path).read(), init_globals)
        #
        # for item in init_globals.items():
        #     var_name = item[0]
        #     var_val = item[1]
        #     if var_name.startswith('CW_'):
        #         if not isinstance(var_val, str):
        #             raise ValueError(f'Compose init set var {var_name} to a non string value {var_val}')
        #         self.env_vars[var_name] = var_val
        #
        # self.name = self.env_vars.get('CW_NAME')

        # self.name =  self.env_vars.get('CW_NAME')

        services_string = self.env_vars.get('CW_SERVICES')
        for service_entry in [e.strip() for e in services_string.split(',') if e.strip()]:
            service_parts = service_entry.split(':')
            service_name = service_parts[0].strip()
            service_dirname = service_parts[1].strip()

            from hapisetup.service import Service
            Service(name=service_name,
                    path=self.get_full_path(service_dirname),
                    compose=self)

        # # load service defs, if any
        # for service_entry in [e.strip() for e in services_string.split(',') if e.strip()]:
        #     service_parts = service_entry.split(':')
        #     service_name = service_parts[0].strip()
        #     service_dirname = service_parts[1].strip()
        #     for fragment in ['', '_project', '_local']:
        #         defs_path = self.path / service_dirname / 'config' / f'init{fragment}_defs.py'
        #         if defs_path.exists():
        #             logging.info(f'Loading {defs_path}')
        #             exec(open(defs_path).read(), self.globals)
        #
        # # instantiate all service objects
        # for service_entry in [e.strip() for e in services_string.split(',') if e.strip()]:
        #     service_parts = service_entry.split(':')
        #     service_name = service_parts[0].strip()
        #     service_dirname = service_parts[1].strip()
        #
        #     from hapisetup.service import Service
        #     Service(name=service_name,
        #             path=self.get_full_path(service_dirname),
        #             compose=self)
        #
        #     init_globals: dict[str, typing.Any] = dict(self.globals)
        #     for fragment in ['', '_project', '_local']:
        #         init_globals['service'] = service
        #         init_path = service.path / 'config' / f'init{fragment}.py'
        #         if init_path.exists():
        #             logging.info(f'Loading {init_path}')
        #             exec(open(init_path).read(), init_globals)
        #             service = init_globals['service']
        #
        #     for item in init_globals.items():
        #         var_name = item[0]
        #         var_val = item[1]
        #         if var_name.startswith('CW_'):
        #             if not isinstance(var_val, str):
        #                 raise ValueError(f'Service {service} set var {var_name} to a non string value {var_val}')
        #             service.env_vars[var_name] = var_val
        #
        #     self.services[service_name] = service
        #
        for service in self.services.values():
            self.cli.add_typer(service.cli, name=service.name)

        hello_typer = typer.Typer(rich_markup_mode="markdown")

        hello_typer.command(name='hi')(self.hi)

        self.cli.add_typer(hello_typer, name='hello')
