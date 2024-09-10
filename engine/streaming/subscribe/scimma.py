import json
import time
import click
import logging
import traceback

from io import BytesIO
from pprint import pprint
import fastavro

from astropy.table import Table
import astropy_healpix as ah
from hop import stream
import numpy as np

def parse_notice(records):
    print(records)

    for record in records:
        try:
            if record['superevent_id'][0] != 'M':
                return
        except:
            print("failed record", record)
            raise

        if record['alert_type'] == 'RETRACTION':
            print(record['superevent_id'], 'was retracted')
            return

        # Respond only to 'CBC' events. Change 'CBC' to 'Burst' to respond to
        # only unmodeled burst events.
        if record['event']['group'] != 'CBC':
            return

        # Parse sky map
        skymap_bytes = record.get('event', {}).pop('skymap')
        if skymap_bytes:
            # Parse skymap directly and print most probable sky location
            skymap = Table.read(BytesIO(skymap_bytes))

            level, ipix = ah.uniq_to_level_ipix(
                skymap[np.argmax(skymap['PROBDENSITY'])]['UNIQ']
            )
            ra, dec = ah.healpix_to_lonlat(ipix, ah.level_to_nside(level),
                                           order='nested')
            print(f'Most probable sky location (RA, Dec) = ({ra.deg}, {dec.deg})')

            # Print some information from FITS header
            print(f'Distance = {skymap.meta["DISTMEAN"]} +/- {skymap.meta["DISTSTD"]}')

        # Print remaining fields
        print('Record:')
        pprint(record)


@click.command("scimma")
@click.option("--topic", default="igwn.gwalert")
def subscribe_scimma(topic):
    with stream.open(f'kafka://kafka.scimma.org/{topic}', 'r') as s:
        for message in s:
            t0 = time.strftime("%Y%m%d_%H%M%S")
        
            print(message.content)

            try:
                parse_notice(message.content)
            except Exception as e:
                print("unable to parse message", e)
                print(traceback.format_exc())

            try:
                with open(f"messages/inbox/scimma_{t0}.json", "wb") as f:
                    json.dump(message.content[0].encode(), f)
            except Exception as e:
                print("unable to save message", e)
                print(traceback.format_exc())



@click.command("test_scimma")
@click.argument("file")
def test_scimma(file):
    # Read the file in bytes mode and then parse it
    with open(file, 'rb') as fo:
        reader = fastavro.reader(fo)
        # LIGO/Virgo/KAGRA notices will only ever contain one record
        record = next(reader)

    parse_notice(record)
