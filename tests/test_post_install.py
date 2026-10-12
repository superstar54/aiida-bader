from types import SimpleNamespace

import pytest
from aiida import orm
from click.testing import CliRunner

from aiida_bader import __main__ as plugin_cli
from aiida_bader import utils


def test_verify_post_install_passes(monkeypatch):
    monkeypatch.setattr(plugin_cli, "load_profile", lambda _profile: None)
    monkeypatch.setattr(utils, "verify_setup", lambda: None)

    result = CliRunner().invoke(plugin_cli.cli, ["verify-post-install"])

    assert result.exit_code == 0
    assert "setup is valid" in result.output


def test_verify_post_install_reports_incomplete_setup(monkeypatch):
    monkeypatch.setattr(plugin_cli, "load_profile", lambda _profile: None)

    def fail_verification():
        raise RuntimeError("AiiDA code bader@localhost is not configured")

    monkeypatch.setattr(utils, "verify_setup", fail_verification)

    result = CliRunner().invoke(plugin_cli.cli, ["verify-post-install"])

    assert result.exit_code != 0
    assert "bader@localhost is not configured" in result.output


def test_verify_setup_does_not_require_named_conda_environment(monkeypatch, tmp_path):
    executable = tmp_path / "bader"
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(0o755)
    code = SimpleNamespace(filepath_executable=str(executable))
    monkeypatch.setattr(
        orm, "load_computer", lambda _label: SimpleNamespace(label="localhost")
    )
    monkeypatch.setattr(orm, "load_code", lambda _label: code)
    monkeypatch.setattr(utils, "pseudo_group_exists", lambda _label: True)
    monkeypatch.setattr(
        utils,
        "conda_env_exists",
        lambda *_args: pytest.fail("verification must use the configured code"),
    )

    utils.verify_setup()


@pytest.mark.parametrize(
    ("path_state", "expected_message"),
    [
        ("unset", "bader@localhost executable is not set"),
        ("missing", "bader@localhost executable is missing"),
        ("directory", "bader@localhost executable is not a file"),
        ("not_executable", "bader@localhost executable is not executable"),
    ],
)
def test_verify_setup_rejects_invalid_registered_executable(
    monkeypatch, tmp_path, path_state, expected_message
):
    executable = tmp_path / "bader"
    if path_state == "unset":
        filepath = None
    elif path_state == "directory":
        executable.mkdir()
        filepath = str(executable)
    elif path_state == "not_executable":
        executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        executable.chmod(0o644)
        filepath = str(executable)
    else:
        filepath = str(executable)
    code = SimpleNamespace(filepath_executable=filepath)
    monkeypatch.setattr(
        orm, "load_computer", lambda _label: SimpleNamespace(label="localhost")
    )
    monkeypatch.setattr(orm, "load_code", lambda _label: code)
    monkeypatch.setattr(utils, "pseudo_group_exists", lambda _label: True)

    with pytest.raises(RuntimeError, match=expected_message):
        utils.verify_setup()
