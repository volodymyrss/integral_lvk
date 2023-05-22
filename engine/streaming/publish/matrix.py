import base64
from io import BytesIO
from jinja2 import Template
from matrix_client.api import MatrixHttpApi
import subprocess

token = subprocess.check_output(["pass", "matrix"]).decode("utf-8").strip()
channel = subprocess.check_output(["pass", "matrix-imma-channel-real"]).decode("utf-8").strip()
# channel = subprocess.check_output(["pass", "matrix-imma-channel"]).decode("utf-8").strip()

matrix = MatrixHttpApi("https://matrix.org", token=token)
response = matrix.send_message(channel, "Hello!")

template = Template("""
{{parse.event_id}} at {{parse.t0_utc}} excesses:
{%- for entry in integralallsky.reportable_excesses -%}
{%- if entry.excess.FAP < 1 %}
at T0+{{entry.excess.rel_s_scale | round(2)}} FAP = {{entry.excess.FAP | round(3)}}
{%- endif -%}
{%- endfor -%}
""")

def publish(data):
    message = template.render(data)
    print(message)
    matrix.send_message(channel, message)

    for k, v in data['integralallsky'].items():
        if k.endswith("_content"):
            uploaded = matrix.media_upload(BytesIO(base64.b64decode(v)), "image/png", k)
            print(uploaded)
            matrix.send_content(channel, uploaded['content_uri'], k, "m.image")