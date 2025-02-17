"""Command line interface for the aiida-bader package.
"""

from aiida.common.exceptions import NotExistent
import subprocess
from aiida.orm import load_code, load_computer
from aiida import load_profile
import shutil
import click


@click.group()
def cli():
    pass


@cli.command(help="Create a conda environment for bader.")
def create_bader_env():
    """Create a conda environment for bader.

    1) check if conda is installed, if not raise an error.
    2) create a conda environment named bader and install the bader package.
    """

    conda_path = shutil.which("conda")
    if not conda_path:
        raise FileNotFoundError(
            "conda is not found in PATH.  \
                                You should update your PATH. If you have not conda in , \
                                your environment, install the code via \
                                `pip install conda --user`."
        )

    command = [
        "conda",
        "create",
        "--name",
        "bader",
        "--channel",
        "conda-forge",
        "bader",
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        raise RuntimeError(
            "An error occurred while creating the conda environment for bader."
        )


@cli.command(help="Setup bader@localhost-hq in the current AiiDA database.")
def setup_bader_code():
    load_profile()
    # load compuer localhost or localhost-hq
    try:
        computer = load_computer("localhost")
    except NotExistent:
        try:
            computer = load_computer("localhost-hq")
        except NotExistent:
            raise NotExistent(
                "localhost or localhost-hq computer not found in the AiiDA database."
            )
    computer_label = computer.label
    try:
        load_code(f"bader@{computer_label}")
    except NotExistent:
        bader_path = shutil.which("bader")
        if not bader_path:
            try:
                create_bader_env()
                bader_path = shutil.which("bader")
            except Exception as e:
                raise RuntimeError(
                    "bader executable not found in PATH. \
                    You should install bader package in your conda environment."
                )

        prepend_text = f'eval "$(conda shell.posix hook)"\\nconda activate bader\\nexport OMP_NUM_THREADS=1'
        command = [
            "verdi",
            "code",
            "create",
            "core.code.installed",
            "--non-interactive",
            "--label",
            "bader",
            "--default-calc-job-plugin",
            "bader.bader",
            "--computer",
            computer_label,
            "prepend_text",
            prepend_text,
            "--filepath-executable",
            bader_path,
        ]

        subprocess.run(command, check=True)
    else:
        print(f"Code bader@{computer_label} is already installed! Nothing to do here.")


if __name__ == "__main__":
    cli()
