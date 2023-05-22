import os
import subprocess
import io
import pathlib
from astropy.io import fits

def sshopen(fn):
    cfn = pathlib.Path("/tmp/sshopen-cache/") / fn.replace("/", "_")
    cfn.parent.mkdir(exist_ok=True)

    try:
        of = fits.open(cfn)
    except:
        cmd = f"ssh login01.astro.unige.ch tar cf - {fn} --dereference | tar xf - -O"
        content = subprocess.check_output(cmd, shell=True)
        f = io.BytesIO(content)

        with open(cfn, "wb") as F:
            F.write(f.read())
        
        try:
            of = fits.open(cfn)
        except Exception as e:
            print("unable to open", str(content)[:100], "cmd was", cmd)
            raise

    return of

def iarc_open(fn):
    f = None

    for prefix in ["/"]:
        try:
            f = fits.open(os.path.join(prefix, fn))
        except IOError:
            pass

    if f is None:
        f = sshopen(fn)

    return f


def iarc_glob(pattern):
    cmd = f"ssh login01.astro.unige.ch ls {pattern}"
    return subprocess.check_output(cmd, shell=True).decode().split("\n")

