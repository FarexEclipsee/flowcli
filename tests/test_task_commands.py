from __future__ import annotations

from flowcli.cli import main


def test_add_and_list_task(runner, cli_env):
    result = runner.invoke(main, ["task", "add", "Write docs", "--project", "flowcli"])
    assert result.exit_code == 0
    assert "Added task #1" in result.output

    result = runner.invoke(main, ["task", "list"])
    assert result.exit_code == 0
    assert "Write docs" in result.output


def test_mark_task_done(runner, cli_env):
    runner.invoke(main, ["task", "add", "Ship release"])
    result = runner.invoke(main, ["task", "done", "1"])
    assert result.exit_code == 0
    assert "marked done" in result.output

    result = runner.invoke(main, ["task", "list", "--status", "open"])
    assert "Ship release" not in result.output


def test_done_on_missing_task_reports_error(runner, cli_env):
    result = runner.invoke(main, ["task", "done", "999"])
    assert "not found" in result.output


def test_rm_task_requires_confirmation(runner, cli_env):
    runner.invoke(main, ["task", "add", "Temp task"])
    result = runner.invoke(main, ["task", "rm", "1"], input="y\n")
    assert result.exit_code == 0
    assert "deleted" in result.output

    result = runner.invoke(main, ["task", "list", "--status", "all"])
    assert "Temp task" not in result.output


def test_list_empty_shows_message(runner, cli_env):
    result = runner.invoke(main, ["task", "list"])
    assert "No tasks found" in result.output
