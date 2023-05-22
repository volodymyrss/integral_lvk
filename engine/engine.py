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

def pick_keys(d, keys):
    return {k:v for k, v in d.items() if k in keys}


def sequence(fn, publish=False, publish_production=True):
    data = {}

    data['parse'] = run_workflow("workflows/parse.ipynb", {'alert_url': fn})

    ivis_input = {'tstart_utc': data['parse']['t0_utc']}
    ivis_input['target_healpix_url'] = data['parse']['skymap_url']
    data['ivis'] = run_workflow("workflows/integral-visibility.ipynb", ivis_input)

    # iobserve_input = pick_keys(data['parse'], ['t0_utc'])
    # run_workflow("workflows/iobserve.ipynb", iobserve_input)

    integralallsky_input = pick_keys(data['parse'], ['t0_utc'])
    # # try:
    integralallsky_input['mode'] = 'scw'
    data['integralallsky'] = run_workflow("workflows/integralallsky.ipynb", integralallsky_input)
    # # except Exception as e:
    # #     integralallsky_input['mode'] = 'rt'
    # #     data['integralallsky'] = run_workflow("workflows/integralallsky.ipynb", integralallsky_input)

    if publish:
        publish_matrix(data, test=publish_production)

    

@click.command("process-file")
@click.argument("fn")
@click.option("--publish/--no-publish", default=False)
@click.option("--publish-prod", is_flag=True, default=False)
def run_sequence(fn, publish, publish_prod):
    sequence(fn, publish=publish, publish_production=publish_prod)
