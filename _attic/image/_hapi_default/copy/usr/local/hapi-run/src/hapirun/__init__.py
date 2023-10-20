import click


@click.command(name='hapi-run')
@click.option('--message')
def hapi_run(**kwargs):
    print("Python hapi" + str(kwargs))
