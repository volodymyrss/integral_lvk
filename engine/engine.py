import time
import click
import logging

from odafunction.executors import default_execute_to_value
from odafunction.func.urifunc import URIipynbFunction
import os

from .streaming.publish import publish as publish_all


def run_workflow(workflow, input):
    f = URIipynbFunction.from_generic_uri("file://" + os.path.abspath(workflow))
    print("found as", f)
    f = f(**input)
    print("found parameters applied as", f)
    return default_execute_to_value(f, cached=True)['output_values']

def pick_keys(d, keys):
    return {k:v for k, v in d.items() if k in keys}


def sequence(fn, publish=False, publish_production=False):
    data = {}

    data['parse'] = run_workflow("workflows/parse.ipynb", {'alert_url': fn})

    if data['parse']['role'] == 'test':
        publish_production = False

    ivis_input = {'tstart_utc': data['parse']['t0_utc']}
    ivis_input['target_healpix_url'] = data['parse']['skymap_url']
    data['ivis'] = run_workflow("workflows/integral-visibility.ipynb", ivis_input)

    # iobserve_input = pick_keys(data['parse'], ['t0_utc'])
    # run_workflow("workflows/iobserve.ipynb", iobserve_input)

    integralallsky_input = pick_keys(data['parse'], ['t0_utc'])
    # # try:
    integralallsky_input['mode'] = 'rt'
    data['integralallsky'] = run_workflow("workflows/integralallsky.ipynb", integralallsky_input)
    # # except Exception as e:
    # #     integralallsky_input['mode'] = 'rt'
    # #     data['integralallsky'] = run_workflow("workflows/integralallsky.ipynb", integralallsky_input)

    if publish:
        publish_all(["hermes", "matrix"], data, test=not publish_production)

    

@click.command("process-file")
@click.argument("fn")
@click.option("--publish/--no-publish", default=False)
@click.option("--publish-prod", is_flag=True, default=False)
def run_sequence(fn, publish, publish_prod):
    sequence(fn, publish=publish, publish_production=publish_prod)


@click.command("process-inbox")
@click.argument("basedir")
@click.option("--publish/--no-publish", default=False)
@click.option("--publish-prod", is_flag=True, default=False)
def run_sequence_loop(basedir, publish, publish_prod):
    inbox = os.path.join(basedir, "inbox")
    outbox = os.path.join(basedir, "archived")
    failbox = os.path.join(basedir, "failbox")    

    print("inbox", inbox)
    print("outbox", outbox)
    print("failbox", failbox)

    while True:

        for fn in os.listdir(inbox):
            if fn.endswith(".data"):
                full_fn = os.path.join(inbox, fn)
                print("processing", full_fn)
                try:
                    sequence(full_fn, publish=publish, publish_production=publish_prod)
                    if publish:
                        os.rename(full_fn, os.path.join(outbox, fn))
                except Exception as e:
                    logging.error("failed to process %s: %s", fn, e)
                    os.rename(full_fn, os.path.join(failbox, fn))

        print("sleeping")

        time.sleep(10)
