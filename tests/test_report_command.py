from __future__ import annotations

from flowcli.cli import main


def test_report_end_to_end(runner, cli_env):
    runner.invoke(main, ["task", "add", "Deep work", "--project", "flowcli"])
    runner.invoke(main, ["timer", "start", "1"])
    runner.invoke(main, ["timer", "stop"])

    result = runner.invoke(main, ["report", "--format", "markdown"])
    assert result.exit_code == 0
    assert "Deep work" in result.output


def test_report_json_format(runner, cli_env):
    runner.invoke(main, ["task", "add", "Deep work"])
    runner.invoke(main, ["timer", "start", "1"])
    runner.invoke(main, ["timer", "stop"])

    result = runner.invoke(main, ["report", "--format", "json"])
    assert result.exit_code == 0
    assert '"description": "Deep work"' in result.output


def test_report_unknown_format_errors(runner, cli_env):
    result = runner.invoke(main, ["report", "--format", "xml"])
    assert result.exit_code == 1
    assert "Unknown export format" in result.output


def test_report_writes_to_file(runner, cli_env, tmp_path):
    runner.invoke(main, ["task", "add", "Deep work"])
    runner.invoke(main, ["timer", "start", "1"])
    runner.invoke(main, ["timer", "stop"])

    out_file = tmp_path / "report.md"
    result = runner.invoke(main, ["report", "--format", "markdown", "--output", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    assert "Deep work" in out_file.read_text()
