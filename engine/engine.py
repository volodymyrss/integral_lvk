import time
import traceback
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


def sequence(fn, publish=False, publish_production=False, ignore_filters=False):
    data = {}

    data['parse'] = run_workflow("workflows/parse.ipynb", {'alert_url': fn})

    print(data['parse'])

    if data['parse']['useful_alert'] != 1 and not ignore_filters:
        print("ignoring not useful alert")
        return
    
    if data['parse']['role'] == 'test':
        #publish_production = False
        print("ignoring test alert")
        return
    
    data['rtstate'] = run_workflow("workflows/rtstate.ipynb", {'t0_utc': data['parse']['t0_utc']})


    if data['rtstate']['prophecy'][1]['expected_data_status'] == 'ONLINE':

        ivis_input = {'tstart_utc': data['parse']['t0_utc']}
        ivis_input['target_healpix_url'] = data['parse']['skymap_url']
        data['ivis'] = run_workflow("workflows/integral-visibility.ipynb", ivis_input)

        # iobserve_input = pick_keys(data['parse'], ['t0_utc'])
        # run_workflow("workflows/iobserve.ipynb", iobserve_input)

        integralallsky_input = pick_keys(data['parse'], ['t0_utc'])
        #integralallsky_input['mode'] = 'scw'
        #integralallsky_input['mode'] = 'rt'
        integralallsky_input['mode'] = 'scw'
        #integralallsky_input['mode'] = 'rt'
        data['integralallsky'] = run_workflow("workflows/integralallsky.ipynb", integralallsky_input)
        # # except Exception as e:
        # #     integralallsky_input['mode'] = 'rt'
        # #     data['integralallsky'] = run_workflow("workflows/integralallsky.ipynb", integralallsky_input)        

    else:
        print("status if offline", data['rtstate'])

    if True:
    #if False:
        try:
            gcn_input = dict(
                datasource="scw",
                gcn_number="XXXXXX",
                name=data['parse']['name'],
                t0_utc=data['parse']['t0_utc'],
                event_kind=data['parse']['event_kind'],
                healpix_url=data['parse']['skymap_url'],
            )
            data['gcn'] = run_workflow("workflows/gcn.ipynb", gcn_input)

            print("gcn", data['gcn'].keys())
            print("gcn_wrapped_text", data['gcn']['gcn_wrapped_text'])
        except Exception as e:
            print("problem with gcn", e)
            raise

    print("data['integralallsky']", data['integralallsky'].keys())
    print("data['integralallsky']['reportable_excesses']", data['integralallsky']['reportable_excesses'])

    if publish:
        publish_all(["hermes", "matrix"], data, test=not publish_production)

    

@click.command("process-file")
@click.argument("fn")
@click.option("--publish/--no-publish", default=False)
@click.option("--publish-prod", is_flag=True, default=False)
@click.option("--ignore-filters", is_flag=True, default=False)
def run_sequence(fn, publish, publish_prod, ignore_filters):

    if fn.startswith("https://"):
        import xmltodict as xd
        import json, requests

        url = fn
        fn = os.getcwd() + "/messages/inbox/" + url.split("/")[-1].split(".")[0] + ".json"
        json.dump(xd.parse(requests.get(url).text), open(fn, "w"))

    sequence(fn, publish=publish, publish_production=publish_prod, ignore_filters=ignore_filters)


@click.command("process-inbox")
@click.argument("basedir")
@click.option("--publish/--no-publish", default=False)
@click.option("--publish-prod", is_flag=True, default=False)
def run_sequence_loop(basedir, publish, publish_prod):
    inbox = os.path.join(basedir, "inbox")
    outbox = os.path.join(basedir, "archived")
    failbox = os.path.join(basedir, "failbox")    
    permafail = os.path.join(basedir, "permafail")

    print("inbox", inbox)
    print("outbox", outbox)
    print("failbox", failbox)

    while True:

        for fn in os.listdir(inbox):
            if fn.endswith(".json") and 'gwnet_LVC_' in fn:
                full_fn = os.path.join(inbox, fn)
                print("processing", full_fn)
                try:
                    sequence(full_fn, publish=publish, publish_production=publish_prod)
                    if publish:
                        os.rename(full_fn, os.path.join(outbox, fn))
                except Exception as e:
                    traceback.print_exc()
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
                os.rename(os.path.join(failbox, failfn), os.path.join(permafail, failfn))


        print(".", end="", flush=True)

        time.sleep(10)
