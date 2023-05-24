import re
import os

from .templates import format


def slug(*args, **kwargs):
    return re.sub("[^0-9a-zA-Z]+", "_", format(*args, **kwargs)['title'])


def publish(destinations, *args, **kwargs):
    test = kwargs.get('test', True)

    for destination in destinations:
        if destination == "matrix":
            from .matrix import publish
        elif destination == "hermes":
            from .hermes import publish
        else:
            raise ValueError(f"Unknown destination {destination}")
                
        print("publishing to", destination)

        published_flag_fn = os.path.join(os.getcwd(), "messages/published", slug(*args, **kwargs) + '-' + destination + "-.published-" + str(test))

        if os.path.exists(published_flag_fn):
            print("already published", published_flag_fn)
            continue
        else:
            r = publish(*args, **kwargs)
            
            os.makedirs(os.path.dirname(published_flag_fn), exist_ok=True)
            with open(published_flag_fn, "w") as f:
                f.write(str(r))