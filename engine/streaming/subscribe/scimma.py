import json
import time
import click
import logging

from io import BytesIO
from pprint import pprint
import fastavro

from astropy.table import Table
import astropy_healpix as ah
from hop import stream
import numpy as np

def parse_notice(record):
    # Only respond to mock events. Real events have GraceDB IDs like
    # S1234567, mock events have GraceDB IDs like M1234567.
    # NOTE NOTE NOTE replace the conditional below with this commented out
    # conditional to only parse real events.
    # if record['superevent_id'][0] != 'S':
    #    return
    if record['superevent_id'][0] != 'M':
        return

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

            try:
                with open(f"messages/inbox/scimma_{t0}.json", "w") as f:
                    json.dump(message.content[0], f)
            except Exception as e:
                print("unable to save message", e)



@click.command("test_scimma")
@click.argument("file")
def test_scimma(file):
    # Read the file in bytes mode and then parse it
    with open(file, 'rb') as fo:
        reader = fastavro.reader(fo)
        # LIGO/Virgo/KAGRA notices will only ever contain one record
        record = next(reader)

    parse_notice(record)
