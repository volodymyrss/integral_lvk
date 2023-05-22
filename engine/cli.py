import logging
import click

from .ops import babysit_realtime

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    cli.add_command(babysit_realtime)
    cli()