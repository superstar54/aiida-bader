"""Command line interface for the aiida-bader package."""

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


@cli.command(help="Verify the Bader post-install setup.")
@click.option("-p", "--profile", default="default", help="AiiDA profile name.")
def verify_post_install(profile):
    from aiida_bader.utils import verify_setup

    load_profile(profile)
    try:
        verify_setup()
    except RuntimeError as error:
        raise click.ClickException(str(error)) from error
    click.echo("Bader post-install setup is valid.")


if __name__ == "__main__":
    cli()
