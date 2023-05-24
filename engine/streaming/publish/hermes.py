# https://hermes.lco.global/api/v0/submit_message/#post-generic-content-form
# https://hermes.lco.global/about

import requests
import subprocess

hermes_submit_url = 'https://hermes.lco.global/api/v0/submit_message/'
HERMES_API_KEY = subprocess.check_output(["pass", "hermes-secret"]).decode("utf-8").strip()

# Authenticate User in Request Headers
headers = {'Authorization': f'Token {HERMES_API_KEY}'}

# Define Your Message Dictionary
message = {
    'topic': 'hermes.test',
    'title': 'Test Title',
    'submitter': 'Volodymyr Savchenko',
    'data': {},
    'message_text': 'Sample Message',
}

# Submit to Hermes
response = requests.post(url=hermes_submit_url, json=message, headers=headers)

print(response)