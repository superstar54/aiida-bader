from aiida.orm import QueryBuilder, Group
import shutil
import subprocess


BASE_URL = "https://github.com/superstar54/aiida-bader/raw/main/data/"


def load_pseudos(structure, pseudo_group="psl_kjpaw_pbesol"):
    """Load the pseudos for the given structure and pseudo group."""
    pseudo_group = (
        QueryBuilder().append(Group, filters={"label": pseudo_group}).one()[0]
    )
    pseudos = {}
    for kind in structure.kinds:
        pseudos[kind.symbol] = next(
            pseudo for pseudo in pseudo_group.nodes if pseudo.label == kind.name
        )
    return pseudos


def create_bader_env():
    """Create a conda environment for bader if it does not already exist."""

    conda_path = shutil.which("conda")
    if not conda_path:
        raise FileNotFoundError(
            "conda is not found in PATH. Please install conda and update your PATH."
        )

    if conda_env_exists("bader"):
        print("Conda environment 'bader' already exists. Skipping creation.")
        return

    command = [
        "conda",
        "create",
        "--name",
        "bader",
        "--channel",
        "conda-forge",
        "bader",
        "--yes",  # Auto-confirm installation
    ]

    try:
        subprocess.run(command, check=True)
        print("Conda environment 'bader' created successfully.")
    except subprocess.CalledProcessError:
        raise RuntimeError(
            "An error occurred while creating the conda environment for bader."
        )


def pseudo_group_exists(group_label):
    groups = (
        QueryBuilder()
        .append(
            Group,
            filters={"label": group_label},
        )
        .all(flat=True)
    )
    return len(groups) > 0 and len(groups[0].nodes) > 0


def conda_env_exists(env_name):
    """Check if a conda environment exists."""
    try:
        result = subprocess.run(
            ["conda", "env", "list"], capture_output=True, text=True, check=True
        )
        return any(env_name in line for line in result.stdout.splitlines())
    except subprocess.CalledProcessError:
        return False


def get_bader_executable():
    """Get the full path of the bader executable inside the conda environment."""
    try:
        result = subprocess.run(
            ["conda", "run", "--name", "bader", "which", "bader"],
            capture_output=True,
            text=True,
            check=True,
        )
        bader_path = result.stdout.strip()
        if not bader_path:
            raise FileNotFoundError("bader executable not found in conda environment.")
        return bader_path
    except subprocess.CalledProcessError:
        raise RuntimeError("Failed to determine the path of the bader executable.")


def install_pseudos():
    import os
    from pathlib import Path
    from aiida_bader.qeapp.model import ConfigurationSettingsModel

    config_instance = ConfigurationSettingsModel()
    for group_label in config_instance.pseudo_group_options:

        if not pseudo_group_exists(group_label):
            print(f"Downloading pseudopotential group '{group_label}'...")
            url = BASE_URL + group_label + ".aiida"
            env = os.environ.copy()
            env["PATH"] = f"{env['PATH']}:{Path.home().joinpath('.local', 'bin')}"

            def run_(*args, **kwargs):
                return subprocess.run(
                    *args, env=env, capture_output=True, check=True, **kwargs
                )

            run_(["verdi", "archive", "import", url, "--no-import-group"])
        else:
            print(f"Pseudopotential group '{group_label}' already exists.")


def setup_bader_code():
    from aiida.orm import load_code, load_computer
    from aiida.common.exceptions import NotExistent

    try:
        computer = load_computer("localhost")
    except NotExistent:
        raise NotExistent("localhost computer not found in the AiiDA database.")

    computer_label = computer.label

    try:
        load_code(f"bader@{computer_label}")
        print(f"Code bader@{computer_label} is already installed! Nothing to do here.")
    except NotExistent:
        create_bader_env()
        bader_path = get_bader_executable()

        prepend_text = f'eval "$(conda shell.posix hook)"\nconda activate bader\nexport OMP_NUM_THREADS=1'
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
            "--prepend-text",
            prepend_text,
            "--filepath-executable",
            bader_path,
        ]

        subprocess.run(command, check=True)
        print(f"Code bader@{computer_label} successfully set up.")
