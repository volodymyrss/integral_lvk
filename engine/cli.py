import logging
import click
from odafunction import logs

from .ops import babysit_realtime
from .engine import run_sequence, run_sequence_loop
from .streaming.cli import streaming

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logs.app_logging.setup()


if __name__ == '__main__':
    cli.add_command(babysit_realtime)
    cli.add_command(run_sequence)
    cli.add_command(run_sequence_loop)
    cli.add_command(streaming)
    cli()