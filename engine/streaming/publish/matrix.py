from jinja2 import Template
from matrix_client.api import MatrixHttpApi
import subprocess

token = subprocess.check_output(["pass", "matrix"]).decode("utf-8").strip()
channel = subprocess.check_output(["pass", "matrix-imma-channel"]).decode("utf-8").strip()

matrix = MatrixHttpApi("https://matrix.org", token=token)
response = matrix.send_message(channel, "Hello!")

template = Template("""
Name: {{name}}
""")

def publish(data):
    print(template.render(data))
    # matrix.send_message(channel, str(data))