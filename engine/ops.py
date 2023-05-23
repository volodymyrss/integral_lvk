import click
import time
import requests
import subprocess
from astropy.time import Time

def run_on_cdcicn02(cmd):
    return subprocess.check_output(["ssh", "cdcicn02", cmd]).decode()

@click.command("babysit-realtime")
@click.option("--interval", default=300)
def babysit_realtime(interval):
    while True:
        try:
            query_range = 10
            lag = 300
            t = Time(Time.now().mjd - lag/24/3600, format='mjd').isot

            print("querying realtime data for", t)
            r = requests.get(f"https://www.astro.unige.ch/mmoda/dispatch-data/gw/integralhk/api/v1.0/rtlc/{t}/{query_range}?json&prophecy")
            r_json = r.json()
            print(t, r_json)

            have_data = len(r_json['lc']['data']) > 1

            if r_json['prophecy'][1]['expected_data_status'] == 'ONLINE':
                print("expecting online!")
                if have_data:
                    print("have online!")
                else:
                    print("no online, will restart service!")
                    run_on_cdcicn02("docker restart spiacs_lcdump")
            else:
                print("expecting offline!")
        except Exception as e:
            print(e)

        print("sleeping for", interval)
        time.sleep(interval)
