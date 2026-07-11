from typer.testing import CliRunner

from meridian_cli.__main__ import app
from tests.helpers import state_dir


def test_quota_command_does_not_traceback(monkeypatch) -> None:
    monkeypatch.setenv("MERIDIAN_HOME", str(state_dir("cli")))
    result = CliRunner().invoke(app, ["quota"])
    assert result.exit_code == 0
    assert "remaining" in result.output
