import logging
import click
from odafunction import logs

from .ops import babysit_realtime
from .engine import run_sequence, run_sequence_loop
from .streaming.cli import streaming

import xmltodict
import requests
import json

def download_url(url="https://gracedb.ligo.org/apiweb/superevents/S240413p/files/S240413p-3-Initial.xml,0"):
    json.dump(
        xmltodict.parse(requests.get(url).text), 
        open("gwnet_LVC__S240413p-3-Initial.json", "w"))

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