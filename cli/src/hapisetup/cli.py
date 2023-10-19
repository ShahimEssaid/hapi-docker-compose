import logging
import os
import pathlib
import sys
import typing
from pathlib import Path

import typer
from typing_extensions import Annotated

from .hapisetup import HapiSetup

logging.basicConfig(level=logging.INFO)

hs: typing.Optional[HapiSetup] = None

cli = typer.Typer(rich_markup_mode="markdown")


@cli.callback()
def hapisetup(
        profiles: Annotated[str, typer.Option(envvar='HS_PROFILES')] = '',
        no_profiles: Annotated[bool, typer.Option('--no_profiles')] = False,
        build_docker_image: Annotated[bool, typer.Option('--build-docker-image')] = True,
        build_hapi: Annotated[bool, typer.Option('--build-hapi')] = False,
        no_out: Annotated[bool, typer.Option('--no-out')] = False,
        no_err: Annotated[bool, typer.Option('--no-err')] = False,
        debug: Annotated[bool, typer.Option('--debug')] = False,
        attach: Annotated[bool, typer.Option('--attach')] = False,

        restart_exit_code: Annotated[int, typer.Option()] = 10,
        setup_path: Annotated[Path, typer.Option()] = Path.cwd(),
        profiles_prefix: Annotated[str, typer.Option(envvar='HS_PROFILES_PREFIX')] = '',
        profiles_suffix: Annotated[str, typer.Option()] = '',
):
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    if debug:
        root.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)

    if profiles:
        os.environ['HS_PROFILES_CMDLINE'] = profiles

    if no_profiles:
        os.environ['HS_PROFILES_CMDLINE'] = ''

    os.environ['HS_PROFILES_PREFIX'] = profiles_prefix
    os.environ['HS_PROFILES_SUFFIX'] = profiles_suffix

    exec(open(f'env/init.py').read())

    global hs
    hs = HapiSetup(setup_path=setup_path,
                   build_docker_image=build_docker_image,
                   build_hapi=build_hapi,
                   stdout=not no_out,
                   stderr=not no_err,
                   restart_exit_code=restart_exit_code,
                   debug=debug,
                   attach=attach)


# =========================
# General commands
# =========================

# @hapisetup.command(name='start')
@cli.command(name='start')
def start():
    logging.info('Running compose up hapi')
    hs.start()


# @hapisetup.command(name='stop')
@cli.command(name='stop')
def stop():
    logging.info('Running compose stop')
    hs.stop()


# @hapisetup.command(name='down')
@cli.command(name='down')
def down():
    logging.info('Running compose down')
    hs.stop()
    hs.down()


@cli.command(name='compose', context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True), add_help_option=False)
# @click.pass_context
def hs_compose(ctx: Annotated[typer.Context, typer.Argument()]):
    """Simply runs docker compose with the command line args specified."""
    hs.compose(ctx.args)


# @hapisetup.command(name='env')
@cli.command(name='env')
def hs_env():
    """Show the effective environment."""
    for name, value in sorted(os.environ.items()):
        print("\t" + name + "=" + value)


@cli.command(name='reset')
def reset(
        pg: Annotated[bool, typer.Option(is_flag=True)] = False,
        es: Annotated[bool, typer.Option(is_flag=True)] = False,
        hapi_target: Annotated[bool, typer.Option(is_flag=True)] = False,
        hapi_logs: Annotated[bool, typer.Option(is_flag=True)] = False,
        hapi_loaders: Annotated[bool, typer.Option(is_flag=True)] = False,
):
    # print(kwargs)
    hs.reset(**locals())


# =========================
# Postgresql commands
# =========================

postgres_cli: typer.Typer = typer.Typer(rich_markup_mode="markdown")
cli.add_typer(postgres_cli, name='postgres')


# @hapisetup.group(name='pg')
@postgres_cli.callback()
def postgres():
    """Postgresql specific subcommands"""
    pass


# @postgresql.command(name='up')
@postgres_cli.command(name='up')
def postgres_up():
    hs.postgres_up()


# @postgresql.command(name='stop')
@postgres_cli.command(name='stop')
def postgres_stop():
    hs.postgres_stop()


# @postgresql.command(name='remove')
@postgres_cli.command(name='rm')
def postgres_rm():
    """Stops and removes the Postgresql container"""
    hs.postgres_stop()
    hs.postgres_rm()


@postgres_cli.command('reset')
def postgres_reset():
    postgres_rm()
    hs.postgres_reset()


# =========================
# Elasticsearch commands
# =========================

es_cli = typer.Typer()
cli.add_typer(es_cli, name='es')


# @hapisetup.group(name='es')
@es_cli.callback()
def elasticsearch():
    """Elasticsearch specific subcommands"""
    pass


# @elasticsearch.command(name='up')
@es_cli.command(name='up')
def elasticsearch_up():
    """Start Elasticsearch"""
    hs.elasticsearch_up()


# @elasticsearch.command(name='stop')
@es_cli.command(name='stop')
def elasticsearch_stop():
    """Stop Elasticsearch"""
    hs.elasticsearch_stop()


# @elasticsearch.command(name='remove')
@es_cli.command(name='rm')
def elasticsearch_rm():
    """Stops and removes the Elasticsearch container"""
    hs.elasticsearch_stop()
    hs.elasticsearch_rm()


# =========================
# Kibana commands
# =========================

# @hapisetup.group(name='kibana')
kibana_cli = typer.Typer(rich_markup_mode="markdown")
cli.add_typer(kibana_cli, name='kibana')


@kibana_cli.callback()
def kibana():
    """Kibana specific subcommands"""
    pass


@kibana_cli.command(name='up')
def kibana_start():
    """Up the Kibana container"""
    hs.kibana_up()


@kibana_cli.command(name='stop')
def kibana_stop():
    """Stop Kibana container"""
    hs.kibana_stop()


@kibana_cli.command(name='rm')
def kibana_rm():
    """Stops and removes the Kibana container"""
    hs.kibana_stop()
    hs.kibana_rm()


# =========================
# HAPI build commands
# =========================

hapi_build_cli = typer.Typer(rich_markup_mode="markdown")
cli.add_typer(hapi_build_cli, name='hapi-build')


@hapi_build_cli.callback()
def hapi_build():
    pass


@hapi_build_cli.command('build')
def hapi_build_build():
    hs.hapi_build_build()


# =========================
# HAPI commands
# =========================

hapi_cli = typer.Typer(rich_markup_mode="markdown")
cli.add_typer(hapi_cli, name='hapi')


@hapi_cli.callback()
def hapi():
    pass


@hapi_cli.command(name='load')
def load(loaders_dir: Annotated[
    pathlib.Path, typer.Option(help='The relative path to a loaders directory under hapi/...')] = pathlib.Path(
        'loaders')):
    hs.hapi_load(loaders_dir)


# =========================
# Janus
# =========================

janusgraph_cli = typer.Typer(rich_markup_mode="markdown")
cli.add_typer(janusgraph_cli, name='janusgraph')


@janusgraph_cli.callback()
def janusgraph():
    """Janusgraph specific subcommands"""
    pass


@janusgraph_cli.command(name='up')
def janusgraph_up():
    """Up the Janusgraph container"""
    hs.janusgraph_up()


@janusgraph_cli.command(name='stop')
def janusgraph_stop():
    """Stop Janusgraph container"""
    hs.janusgraph_stop()


@janusgraph_cli.command(name='rm')
def janusgrapy_rm():
    """Stops and removes the Janusgraph container"""
    hs.janusgraph_stop()
    hs.janusgraph_rm()


# =========================
# Cassandra
# =========================

cassandra_cli = typer.Typer(rich_markup_mode="markdown")
cli.add_typer(cassandra_cli, name='cassandra')


@cassandra_cli.callback()
def cassandra():
    """Cassandra specific subcommands"""
    pass


@cassandra_cli.command(name='up')
def cassandra_up():
    """Up the Cassandra container"""
    hs.cassandra_up()


@cassandra_cli.command(name='stop')
def cassandra_stop():
    """Stop Cassandra container"""
    hs.cassandra_stop()


@cassandra_cli.command(name='rm')
def cassandra_rm():
    """Stops and removes the Janusgraph container"""
    hs.cassandra_stop()
    hs.cassandra_rm()


# =========================
# Hidden
# =========================


@cli.command(name='test', hidden=True)
# @click.option('--arg', multiple=True, default=[])
def test(arg: Annotated[typing.Optional[typing.List[str]], typer.Option()] = None):
    if arg is None:
        arg = []
    print(f'Value: {arg}')
    print(f'Type: {type(arg)}')
