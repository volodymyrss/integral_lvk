

def publish_scimma():
    from hop.robust_publisher import RobustProducer

    with RobustProducer("kafka://hostname:port/topic") as publisher:
        for message in messages:
            publisher.write(message)
