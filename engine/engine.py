import click
import logging

from odafunction.executors import default_execute_to_value
from odafunction.func.urifunc import URIipynbFunction
import os

from .streaming.publish.matrix import publish as publish_matrix


def run_workflow(workflow, input):
    f = URIipynbFunction.from_uri("file://" + os.path.abspath(workflow))
    print("found as", f)
    f = f(**input)
    print("found parameters applied as", f)
    return default_execute_to_value(f, cached=True)['output_values']

def sequence(fn, publish=False, publish_production=True):
    data = {}

    data['parse'] = run_workflow("workflows/parse.ipynb", {'alert_url': fn})

    # run_workflow("workflows/iobserve.ipynb", input)
    
    data['integralallsky'] = run_workflow("workflows/integralallsky.ipynb", 
                 {k:v for k, v in data['parse'].items() if k in ['t0_utc']})

    if publish:
        publish_matrix(data, test=publish_production)

    

@click.group()
@click.version_option()
@click.option("--debug", "-d", is_flag=True, help="Enables debug mode.")
def cli(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

@cli.command("process-file")
@click.argument("fn")
@click.option("--publish/--no-publish", default=False)
@click.option("--publish-prod", is_flag=True, default=False)
def run_sequence(fn, publish, publish_prod):
    sequence(fn, publish=publish, publish_production=publish_prod)

if __name__ == "__main__":
    cli.add_command(run_sequence)
    cli()