import typing
from os import environ
from pathlib import Path
import logging

import typer
from typing_extensions import Annotated


class Compose:
    def __init__(self, /, *,
                 compose_path: Path,
                 ):
        self.path: Path = compose_path.absolute().resolve()
        from hapisetup.service import Service
        self.services: dict[str, Service] = {}
        self.profiles: list[str] = []
        self.cli: typer.Typer = typer.Typer(rich_markup_mode="markdown")
        self.globals = {'compose': self,
                        'Compose': Compose,
                        'Service': Service}

        @self.cli.callback()
        def dc_cli():
            print(f'============ DC cli callback ran on  {self} ')

    def init(self):

        # load compose defs, if any
        for fragment in ['', '_project', '_local']:
            defs_path = self.path / 'config' / f'init{fragment}_defs.py'
            if defs_path.exists():
                logging.info(f'Loading {defs_path}')
                exec(open(defs_path).read(), self.globals)

        # load compose inits, if any
        init_globals = dict(self.globals)
        for fragment in ['', '_project', '_local']:
            init_path = self.path / 'config' / f'init{fragment}.py'
            if init_path.exists():
                logging.info(f'Loading {init_path}')
                exec(open(init_path).read(), init_globals)

        services_string = environ.get('DC_SERVICES', '')

        # load service defs, if any
        for service_entry in [e.strip() for e in services_string.split(',') if e.strip()]:
            service_parts = service_entry.split(':')
            service_name = service_parts[0].strip()
            service_dirname = service_parts[1].strip()
            for fragment in ['', '_project', '_local']:
                defs_path = self.path / service_dirname / 'config' / f'init{fragment}_defs.py'
                if defs_path.exists():
                    logging.info(f'Loading {defs_path}')
                    exec(open(defs_path).read(), self.globals)

        # instantiate all service objects
        for service_entry in [e.strip() for e in services_string.split(',') if e.strip()]:
            service_parts = service_entry.split(':')
            service_name = service_parts[0].strip()
            service_dirname = service_parts[1].strip()

            from hapisetup.service import Service
            service: Service = Service(name=service_name,
                                       path=self.get_full_path(service_dirname),
                                       compose=self)
            self.services[service_name] = service

        services = list(self.services.values())
        for service in services:
            init_globals = dict(self.globals)
            for fragment in ['', '_project', '_local']:
                init_globals['service'] = self.services[service.name]
                init_path = service.path / 'config' / f'init{fragment}.py'
                if init_path.exists():
                    logging.info(f'Loading {init_path}')
                    exec(open(init_path).read(), init_globals)
                    self.services[service.name] = init_globals['service']

        for service in self.services.values():
            self.cli.add_typer(service.cli, name=service.name)

        hello_typer = typer.Typer(rich_markup_mode="markdown")

        @hello_typer.command()
        def hi():
            print(' =========== hello')

        self.cli.add_typer(hello_typer, name='hello')

    def get_full_path(self, relative_path: typing.Union[str, Path]):
        if isinstance(relative_path, str):
            relative_path = Path(relative_path)
        if relative_path.is_absolute():
            raise ValueError(f'Relative path is absolute while getting full path: {relative_path}')
        return (self.path / relative_path).resolve()

    def get_relative_path(self, other_path: typing.Union[str, Path]):
        if isinstance(other_path, str):
            other_path = Path(other_path)
        other_path = other_path.absolute().resolve()
        if other_path.is_relative_to(self.path):
            return other_path.relative_to(self.path)
        else:
            raise ValueError(f'Path is not relative to compose path: {other_path}')
