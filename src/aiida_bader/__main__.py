"""Command line interface for the aiida-bader package.
"""

from aiida.common.exceptions import NotExistent
import subprocess
from aiida.orm import load_code, load_computer
from aiida import load_profile
import click
from aiida_bader.utils import install_pseudos, setup_bader_code


@click.group()
def cli():
    pass


@cli.command(help="Setup bader@localhost in the current AiiDA database.")
def setup_code():

    load_profile()
    setup_bader_code()


@cli.command(help="Import the PAW pseudopotentials into the AiiDA database.")
def setup_pseudos():

    load_profile()
    install_pseudos()


@cli.command(
    help="Setup bader@localhost and import the PAW pseudopotentials into the AiiDA database."
)
def post_install():
    from aiida_bader.utils import install_pseudos, setup_bader_code

    load_profile()

    setup_bader_code()
    install_pseudos()


if __name__ == "__main__":
    cli()
