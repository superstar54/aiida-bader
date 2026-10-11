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


def test_verify_setup_does_not_require_named_conda_environment(monkeypatch):
    code = SimpleNamespace(filepath_executable="/usr/bin/bader")
    monkeypatch.setattr(
        orm, "load_computer", lambda _label: SimpleNamespace(label="localhost")
    )
    monkeypatch.setattr(orm, "load_code", lambda _label: code)
    monkeypatch.setattr(utils.shutil, "which", lambda _executable: "/usr/bin/bader")
    monkeypatch.setattr(utils, "pseudo_group_exists", lambda _label: True)
    monkeypatch.setattr(
        utils,
        "conda_env_exists",
        lambda *_args: pytest.fail("verification must use the configured code"),
    )

    utils.verify_setup()


def test_verify_setup_rejects_missing_registered_executable(monkeypatch):
    code = SimpleNamespace(filepath_executable="/missing/bader")
    monkeypatch.setattr(
        orm, "load_computer", lambda _label: SimpleNamespace(label="localhost")
    )
    monkeypatch.setattr(orm, "load_code", lambda _label: code)
    monkeypatch.setattr(utils.shutil, "which", lambda _executable: None)
    monkeypatch.setattr(utils, "pseudo_group_exists", lambda _label: True)

    with pytest.raises(RuntimeError, match="Bader executable is missing"):
        utils.verify_setup()
