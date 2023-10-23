import signal
from pathlib import Path
from subprocess import Popen
from typing import Annotated, Any

import typer
from typer import Typer

cli: Typer = Typer(add_help_option=True)

print('running hapi cli')

current_process = None
terminated = False


def get_current_process() -> Any:
    global current_process
    return current_process


@cli.command()
def run(
        build: Annotated[bool, typer.Option()] = False,
        build_always: Annotated[bool, typer.Option()] = False,
        build_type: Annotated[str, typer.Option()] = 'git',
        build_repo: Annotated[str, typer.Option()] = 'https://github.com/hapifhir/hapi-fhir-jpaserver-starter.git',
        build_ref: Annotated[str, typer.Option()] = 'refs/tags/image/v6.8.3',
        build_command: Annotated[str, typer.Option()] = 'mvn -U -Pboot -DskipTests clean package',
        message: Annotated[str, typer.Option()] = 'default message',
        load: Annotated[bool, typer.Option()] = False,
        load_zip_dir: Annotated[Path, typer.Option()] = None,
        load_unzip_dir: Annotated[Path, typer.Option()] = None
):
    global current_process, terminated

    def sigterm(some_signal, *args, **kwargs):
        global  terminated
        print('=============  SIG TERM called  in hapi  ============')
        process = get_current_process()
        if process:
            process.send_signal(signal.SIGTERM)
        terminated = True

    signal.signal(signal.SIGTERM, sigterm)

    if load:
        if not (load_zip_dir and load_unzip_dir):
            raise ValueError(f'Loading zip or unzip directories not specified')

    if (build or not Path('/hapi/ROOT.war').exists()) and not terminated:
        args = ['hapisetup-hapi-build', '--build']
        kwargs = {'stdout': None, 'stderr': None}
        hapi_build_process = Popen(args, cwd='/hapibuild', **kwargs)
        current_process = hapi_build_process
        hapi_build_process.wait()

    if not terminated:
        args = ['hapisetup-hapi-run']
        kwargs = {'stdout': None, 'stderr': None}
        # try:
        hapi_run_process = Popen(args, cwd='/hapi', **kwargs)
        current_process = hapi_run_process

    if not terminated:
        args = ['hapisetup-hapi-cli-install']
        hapi_cli_install = Popen(args, cwd='/hapi', **kwargs)
        current_process = hapi_cli_install
        hapi_cli_install.wait()

    if load and not terminated:
        args = ['hapisetup-hapi-load', str(load_zip_dir), str(load_unzip_dir)]
        hapi_load = Popen(args, cwd='/hapi', **kwargs)
        current_process = hapi_load
        hapi_load.wait()

    hapi_run_process.wait()
