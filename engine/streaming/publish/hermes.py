# https://hermes.lco.global/api/v0/submit_message/#post-generic-content-form
# https://hermes.lco.global/about

import requests
import subprocess
from .templates import format

hermes_submit_url = 'https://hermes.lco.global/api/v0/submit_message/'
HERMES_API_KEY = subprocess.check_output(["pass", "hermes-secret"]).decode("utf-8").strip()

# Authenticate User in Request Headers
headers = {'Authorization': f'Token {HERMES_API_KEY}'}

def publish(data, test):
    sections = format(data, test)

    if test:
        topic = 'hermes.test'
        submitter = 'Volodymyr Savchenko'
    else:
        topic = 'hermes.message'
        submitter = 'Volodymyr Savchenko'

    title = sections['title']
    message_text = sections['body']
    
    message = {
        'topic': topic,
        'title': title,
        'submitter': submitter,
        'data': {},
        'message_text': message_text,
    }

    print(list(data.keys()))

    response = requests.post(url=hermes_submit_url, json=message, headers=headers)

    print(response, response.text)