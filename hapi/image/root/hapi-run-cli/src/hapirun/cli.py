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
    if build:
        args = ['hapisetup-hapi-build', '--build']
        kwargs = {'stdout': None, 'stderr': None}
        popen: Popen = Popen(args, cwd='/hapibuild', **kwargs)
        popen.wait()
    else:
        print('no build')
