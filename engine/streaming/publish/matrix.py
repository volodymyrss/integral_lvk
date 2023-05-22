import base64
from io import BytesIO
from jinja2 import Template
from matrix_client.api import MatrixHttpApi
import subprocess

token = subprocess.check_output(["pass", "matrix"]).decode("utf-8").strip()
channel_real = subprocess.check_output(["pass", "matrix-imma-channel-real"]).decode("utf-8").strip()
channel_test = subprocess.check_output(["pass", "matrix-imma-channel"]).decode("utf-8").strip()

matrix = MatrixHttpApi("https://matrix.org", token=token)

template = Template("""
{{parse.event_id}} at {{parse.t0_utc}}

{% if integralallsky %}
SPI-ACS excesses:
{%- for entry in integralallsky.reportable_excesses -%}
{%- if entry.excess.FAP < 1 %}
at T0+{{entry.excess.rel_s_scale | round(2)}} FAP = {{entry.excess.FAP | round(3)}}
{%- endif -%}
{%- endfor -%}
{% endif %}

{% if ivis %}
{% endif %}

""")

def publish(data, test=True):
    message = template.render(data)
    print(message)

    channel = get_a_room(f'INTEGRAL-{data["parse"]["event_id"]}')
        
    matrix.send_message(channel, message)

    for section in ['integralallsky', 'ivis']:
        if section in data:
            for k, v in data[section].items():
                if k.endswith("_content"):
                    uploaded = matrix.media_upload(BytesIO(base64.b64decode(v)), "image/png", k)
                    print(uploaded)
                    matrix.send_content(channel, uploaded['content_uri'], k, "m.image")


def get_a_room(room_alias):
    try:
        channel = matrix.create_room(room_alias)['room_id']
    except Exception as e:
        print("failed to create room due to", e)
        channel = f"#{room_alias}:matrix.org"
    
    try:
        channel = matrix.join_room(channel)['room_id']
        print("room join", channel)
    except Exception as e:
        print("failed to join room due to", e)

    return channel
