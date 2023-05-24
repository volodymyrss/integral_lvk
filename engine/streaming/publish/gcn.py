# https://gcn.nasa.gov/docs/producers

from gcn_kafka import Producer
# Connect as a producer.
# Warning: don't share the client secret with others.
producer = Producer(client_id='fill me in', client_secret='fill me in')
# any topic starting with 'mission.'
topic = 'gcn.notices.mission.example'
data = b'...'  # any bytes
producer.produce(topic, data)