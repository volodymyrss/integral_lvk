import logging
import click
from .subscribe.gcn import subscribe_gcn
from .subscribe.scimma import subscribe_scimma, test_scimma

logger = logging.getLogger(__name__)

@click.group()
def streaming():
    pass

streaming.add_command(subscribe_gcn)
streaming.add_command(subscribe_scimma)
streaming.add_command(test_scimma)

if __name__ == "__main__":
    streaming()