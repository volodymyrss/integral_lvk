import json
import logging
import os
import click
import xmltodict

from gcn_kafka import Consumer
import subprocess

logger = logging.getLogger(__name__)

def get_pass(name):
    return subprocess.check_output(["pass", name]).decode().strip()


# Connect as a consumer.
consumer = Consumer(client_id=get_pass("gcn-kafla-id"),
                    client_secret=get_pass("gcn-kafla-secret"))

# TODO: add replay from last treated message

# Subscribe to topics and receive alerts
consumer.subscribe(['gcn.classic.voevent.INTEGRAL_REFINED',
                    'gcn.classic.voevent.INTEGRAL_SPIACS',
                    'gcn.classic.voevent.IPN_RAW',
                    # 'gcn.classic.text.LVC_EARLY_WARNING',
                    'gcn.classic.voevent.LVC_TEST',
                    'gcn.classic.voevent.LVC_INITIAL',
                    'gcn.classic.voevent.LVC_PRELIMINARY'])

@click.command()
@click.option('--debug/--no-debug', default=False)
def main(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # consumer.seek('gcn.classic.voevent.INTEGRAL_REFINED', 0)

    while True:
        for message in consumer.consume(timeout=1):
            value = message.value()
            logger.info("got message %s value %s", message, value)

            try:
                value_json = xmltodict.parse(value['content'])
                os.makedirs("messages/inbox", exist_ok=True)
                with open("messages/inbox/%s.json" % value_json['ivorn'], "w") as f:
                    json.dump(value, f)
            except Exception as e:
                logger.error("unable to save message %s", e)


if __name__ == '__main__':
    main()