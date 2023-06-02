import time
import click
import logging

from concurrent.futures import ThreadPoolExecutor


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


def publish(data, test=True):
    if data['parse']['role'] == 'test':
        test = True

    publish_all(["hermes", "matrix"], data, test=test)

def sequence(fn, publish=False, publish_production=False):
    data = {}

    pool = ThreadPoolExecutor()
    
    parse_task = pool.submit(run_workflow, "workflows/parse.ipynb", {'alert_url': fn})
    pool.submit(publish, dict(parse=parse_task.result()), test=not publish_production)

    rtstate_task = pool.submit(run_workflow("workflows/rtstate.ipynb", {'t0_utc': parse_task.result()['t0_utc']}))
    pool.submit(publish, dict(rtstate=rtstate_task.result()), test=not publish_production)

    # if data['rtstate']['prophecy'][1]['expected_data_status'] == 'ONLINE':

    #     ivis_input = {'tstart_utc': data['parse']['t0_utc']}
    #     ivis_input['target_healpix_url'] = data['parse']['skymap_url']
    #     data['ivis'] = run_workflow("workflows/integral-visibility.ipynb", ivis_input)

    #     # iobserve_input = pick_keys(data['parse'], ['t0_utc'])
    #     # run_workflow("workflows/iobserve.ipynb", iobserve_input)

    #     integralallsky_input = pick_keys(data['parse'], ['t0_utc'])
    #     # # try:
    #     integralallsky_input['mode'] = 'rt'
    #     data['integralallsky'] = run_workflow("workflows/integralallsky.ipynb", integralallsky_input)
    #     # # except Exception as e:
    #     # #     integralallsky_input['mode'] = 'rt'
    #     # #     data['integralallsky'] = run_workflow("workflows/integralallsky.ipynb", integralallsky_input)
    # else:
    #     print("status if offline", data['rtstate'])

    # if publish:
    #     publish_all(["hermes", "matrix"], data, test=not publish_production)

    

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

        for failfn in os.listdir(failbox):
            try:
                age_s = time.time() - time.mktime(time.strptime(failfn, "gcn_%Y%m%d_%H%M%S.data"))
                if age_s < 1200:
                    print("failure forgiven", failfn)
                    os.rename(os.path.join(failbox, failfn), os.path.join(inbox, failfn))
     #           else:
    #                print("failure too old", age_s, failfn)
            except Exception as e:
                print("failure unparsable", failfn, e)


        print(".", end="", flush=True)

        time.sleep(10)
