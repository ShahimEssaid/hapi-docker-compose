import signal
from subprocess import Popen
from typing import Annotated

import typer
from typer import Typer

cli: Typer = Typer(add_help_option=True)

print('running hapi cli')


#
# @cli.callback()
# def callback(invoke_without_command=True):
#     print('ran callback')


@cli.command()
def run(
        build: Annotated[bool, typer.Option()] = False,
        build_always: Annotated[bool, typer.Option()] = False,
        build_type: Annotated[str, typer.Option()] = 'git',
        build_repo: Annotated[str, typer.Option()] = 'https://github.com/hapifhir/hapi-fhir-jpaserver-starter.git',
        build_ref: Annotated[str, typer.Option()] = 'refs/tags/image/v6.8.3',
        build_command: Annotated[str, typer.Option()] = 'mvn -U -Pboot -DskipTests clean package',
        message: Annotated[str, typer.Option()] = 'default message'
):
    global popen
    if build:
        args = ['hapisetup-hapi-build', '--build']
        kwargs = {'stdout': None, 'stderr': None}
        popen = Popen(args, cwd='/hapibuild', **kwargs)
        popen.wait()

    args = ['hapisetup-hapi-run']
    kwargs = {'stdout': None, 'stderr': None}
    # try:
    popen = Popen(args, cwd='/hapi', **kwargs)

    def sigint(some_signal, *args, **kwargs):
        print('=============  SIG INT called  in hapi  ============')
        popen.send_signal(signal.SIGINT)

    signal.signal(signal.SIGINT, sigint)

    def sigterm(some_signal, *args, **kwargs):
        print('=============  SIG TERM called  in hapi  ============')
        popen.send_signal(signal.SIGTERM)

    signal.signal(signal.SIGTERM, sigterm)

    popen.wait()
    # except KeyboardInterrupt:
    #     print('=====================  caught signal ==================== ')
    #     popen.send_signal(signal.SIGINT)
    #     popen.wait()
