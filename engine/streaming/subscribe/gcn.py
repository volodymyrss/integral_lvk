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

# # Subscribe to topics and receive alerts
# consumer.subscribe(['gcn.classic.voevent.INTEGRAL_REFINED',
#                     'gcn.classic.voevent.INTEGRAL_SPIACS',
#                     'gcn.classic.voevent.IPN_RAW',
#                     'gcn.classic.text.LVC_EARLY_WARNING',
#                     #'gcn.classic.voevent.LVC_TEST',
#                     'gcn.classic.voevent.LVC_INITIAL',
#                     'gcn.classic.voevent.LVC_PRELIMINARY',
#                     'gcn.classic.voevent.',
#                     ])

consumer.subscribe(['gcn.classic.text.AGILE_GRB_GROUND',
                    'gcn.classic.text.AGILE_GRB_POS_TEST',
                    'gcn.classic.text.AGILE_GRB_REFINED',
                    'gcn.classic.text.AGILE_GRB_WAKEUP',
                    'gcn.classic.text.AGILE_MCAL_ALERT',
                    'gcn.classic.text.AGILE_POINTDIR',
                    'gcn.classic.text.AGILE_TRANS',
                    'gcn.classic.text.AMON_ICECUBE_COINC',
                    'gcn.classic.text.AMON_ICECUBE_EHE',
                    'gcn.classic.text.AMON_ICECUBE_HESE',
                    'gcn.classic.text.AMON_NU_EM_COINC',
                    'gcn.classic.text.CALET_GBM_FLT_LC',
                    'gcn.classic.text.CALET_GBM_GND_LC',
                    'gcn.classic.text.FERMI_GBM_ALERT',
                    'gcn.classic.text.FERMI_GBM_FIN_POS',
                    'gcn.classic.text.FERMI_GBM_FLT_POS',
                    'gcn.classic.text.FERMI_GBM_GND_POS',
                    'gcn.classic.text.FERMI_GBM_LC',
                    'gcn.classic.text.FERMI_GBM_POS_TEST',
                    'gcn.classic.text.FERMI_GBM_SUBTHRESH',
                    'gcn.classic.text.FERMI_GBM_TRANS',
                    'gcn.classic.text.FERMI_LAT_GND',
                    'gcn.classic.text.FERMI_LAT_MONITOR',
                    'gcn.classic.text.FERMI_LAT_OFFLINE',
                    'gcn.classic.text.FERMI_LAT_POS_DIAG',
                    'gcn.classic.text.FERMI_LAT_POS_INI',
                    'gcn.classic.text.FERMI_LAT_POS_TEST',
                    'gcn.classic.text.FERMI_LAT_POS_UPD',
                    'gcn.classic.text.FERMI_LAT_TRANS',
                    'gcn.classic.text.FERMI_POINTDIR',
                    'gcn.classic.text.FERMI_SC_SLEW',
                    'gcn.classic.text.GECAM_FLT',
                    'gcn.classic.text.GECAM_GND',
                    'gcn.classic.text.ICECUBE_ASTROTRACK_BRONZE',
                    'gcn.classic.text.ICECUBE_ASTROTRACK_GOLD',
                    'gcn.classic.text.ICECUBE_CASCADE',
                    'gcn.classic.text.INTEGRAL_OFFLINE',
                    'gcn.classic.text.INTEGRAL_POINTDIR',
                    'gcn.classic.text.INTEGRAL_REFINED',
                    'gcn.classic.text.INTEGRAL_SPIACS',
                    'gcn.classic.text.INTEGRAL_WAKEUP',
                    'gcn.classic.text.INTEGRAL_WEAK',
                    'gcn.classic.text.IPN_POS',
                    'gcn.classic.text.IPN_RAW',
                    'gcn.classic.text.IPN_SEG',
                    'gcn.classic.text.LVC_COUNTERPART',
                    'gcn.classic.text.LVC_EARLY_WARNING',
                    'gcn.classic.text.LVC_INITIAL',
                    'gcn.classic.text.LVC_PRELIMINARY',
                    'gcn.classic.text.LVC_RETRACTION',
                    'gcn.classic.text.LVC_TEST',
                    'gcn.classic.text.LVC_UPDATE',
                    'gcn.classic.text.MAXI_KNOWN',
                    'gcn.classic.text.MAXI_TEST',
                    'gcn.classic.text.MAXI_UNKNOWN',
                    'gcn.classic.text.SWIFT_ACTUAL_POINTDIR',
                    'gcn.classic.text.SWIFT_BAT_ALARM_LONG',
                    'gcn.classic.text.SWIFT_BAT_ALARM_SHORT',
                    'gcn.classic.text.SWIFT_BAT_GRB_ALERT',
                    'gcn.classic.text.SWIFT_BAT_GRB_LC',
                    'gcn.classic.text.SWIFT_BAT_GRB_LC_PROC',
                    'gcn.classic.text.SWIFT_BAT_GRB_POS_ACK',
                    'gcn.classic.text.SWIFT_BAT_GRB_POS_NACK',
                    'gcn.classic.text.SWIFT_BAT_GRB_POS_TEST',
                    'gcn.classic.text.SWIFT_BAT_KNOWN_SRC',
                    'gcn.classic.text.SWIFT_BAT_MONITOR',
                    'gcn.classic.text.SWIFT_BAT_QL_POS',
                    'gcn.classic.text.SWIFT_BAT_SCALEDMAP',
                    'gcn.classic.text.SWIFT_BAT_SLEW_POS',
                    'gcn.classic.text.SWIFT_BAT_SUB_THRESHOLD',
                    'gcn.classic.text.SWIFT_BAT_SUBSUB',
                    'gcn.classic.text.SWIFT_BAT_TRANS',
                    'gcn.classic.text.SWIFT_FOM_OBS',
                    'gcn.classic.text.SWIFT_FOM_PPT_ARG_ERR',
                    'gcn.classic.text.SWIFT_FOM_SAFE_POINT',
                    'gcn.classic.text.SWIFT_FOM_SLEW_ABORT',
                    'gcn.classic.text.SWIFT_POINTDIR',
                    'gcn.classic.text.SWIFT_SC_SLEW',
                    'gcn.classic.text.SWIFT_TOO_FOM',
                    'gcn.classic.text.SWIFT_TOO_SC_SLEW',
                    'gcn.classic.text.SWIFT_UVOT_DBURST',
                    'gcn.classic.text.SWIFT_UVOT_DBURST_PROC',
                    'gcn.classic.text.SWIFT_UVOT_EMERGENCY',
                    'gcn.classic.text.SWIFT_UVOT_FCHART',
                    'gcn.classic.text.SWIFT_UVOT_FCHART_PROC',
                    'gcn.classic.text.SWIFT_UVOT_POS',
                    'gcn.classic.text.SWIFT_UVOT_POS_NACK',
                    'gcn.classic.text.SWIFT_XRT_CENTROID',
                    'gcn.classic.text.SWIFT_XRT_EMERGENCY',
                    'gcn.classic.text.SWIFT_XRT_IMAGE',
                    'gcn.classic.text.SWIFT_XRT_IMAGE_PROC',
                    'gcn.classic.text.SWIFT_XRT_LC',
                    'gcn.classic.text.SWIFT_XRT_POSITION',
                    'gcn.classic.text.SWIFT_XRT_SPECTRUM',
                    'gcn.classic.text.SWIFT_XRT_SPECTRUM_PROC',
                    'gcn.classic.text.SWIFT_XRT_SPER',
                    'gcn.classic.text.SWIFT_XRT_SPER_PROC',
                    'gcn.classic.text.SWIFT_XRT_THRESHPIX',
                    'gcn.classic.text.SWIFT_XRT_THRESHPIX_PROC',
                    'gcn.classic.text.AAVSO',
                    'gcn.classic.text.ALEXIS_SRC',
                    'gcn.classic.text.BRAD_COORDS',
                    'gcn.classic.text.CBAT',
                    'gcn.classic.text.COINCIDENCE',
                    'gcn.classic.text.COMPTEL_SRC',
                    'gcn.classic.text.DOW_TOD',
                    'gcn.classic.text.GRB_CNTRPART',
                    'gcn.classic.text.GRB_COORDS',
                    'gcn.classic.text.GRB_FINAL',
                    'gcn.classic.text.GWHEN_COINC',
                    'gcn.classic.text.HAWC_BURST_MONITOR',
                    'gcn.classic.text.HUNTS_SRC',
                    'gcn.classic.text.KONUS_LC',
                    'gcn.classic.text.MAXBC',
                    'gcn.classic.text.MILAGRO_POS',
                    'gcn.classic.text.MOA',
                    'gcn.classic.text.OGLE',
                    'gcn.classic.text.SIMBADNED',
                    'gcn.classic.text.SK_SN',
                    'gcn.classic.text.SNEWS',
                    'gcn.classic.text.SUZAKU_LC',
                    'gcn.classic.text.TEST_COORDS'])


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
                    
