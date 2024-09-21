import json
import logging
import os
import re
import time
import click
import xmltodict

from gcn_kafka import Consumer
import subprocess

logger = logging.getLogger(__name__)

def get_pass(name):
    envname = "ILVK_" + re.sub("[^A-Z0-9]+", "_", name.upper())

    logger.warning("looking for %s", envname)

    if value := os.getenv(envname):
        return value
    return subprocess.check_output(["pass", name]).decode().strip()


# Connect as a consumer.
consumer = Consumer(client_id=get_pass("gcn-kafla-id"),
                    client_secret=get_pass("gcn-kafla-secret"))

# TODO: add replay from last treated message

# Subscribe to topics and receive alerts
consumer.subscribe(['gcn.classic.voevent.INTEGRAL_REFINED',
                    'gcn.classic.voevent.INTEGRAL_SPIACS',
                    'gcn.classic.voevent.IPN_RAW',
                    'gcn.classic.text.LVC_EARLY_WARNING',
                    #'gcn.classic.voevent.LVC_TEST',
                    'gcn.classic.voevent.LVC_INITIAL',
                    'gcn.classic.voevent.LVC_PRELIMINARY',
                    ])


    # consumer.seek('gcn.classic.voevent.INTEGRAL_REFINED', 0)


@click.command("gcn")
def subscribe_gcn():
    while True:
        logger.info("still streaming gcns")
        for message in consumer.consume(timeout=10):
            value = message.value()
            logger.info("got message %s value %s", message, value)

            t0 = time.strftime("%Y%m%d_%H%M%S")

            try:
                value_json = xmltodict.parse(value)
                os.makedirs("messages/inbox", exist_ok=True)
                label = re.sub("[^0-9a-zA-Z]", "_", value_json['voe:VOEvent']['@ivorn'])
                fn = f"messages/inbox/{t0}_{label}.json"                
                with open(fn, "w") as f:
                    json.dump(value_json, f)
                logger.info("saved message to %s", fn)

            except Exception as e:
                logger.error("unable to save message %s", e)
                while True:
                    try:
                        with open(f"messages/inbox/gcn_{t0}.data", "wb") as f:
                            f.write(value)
                    except Exception as e:
                        logger.error("problem saving file due to %s, retrying", e)
#                        time.sleep(10)
                        continue
                    
