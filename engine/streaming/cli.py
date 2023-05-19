import logging
import click
from .gcn import subscribe_gcn
from .scimma import subscribe_scimma, test_scimma

logger = logging.getLogger(__name__)

@click.group()
@click.option('--debug/--no-debug', default=False)
def main(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


main.add_command(subscribe_gcn)
main.add_command(subscribe_scimma)
main.add_command(test_scimma)

if __name__ == "__main__":
    main()