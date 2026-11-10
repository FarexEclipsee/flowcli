from __future__ import annotations

from flowcli.cli import main


def test_start_and_stop_timer(runner, cli_env):
    runner.invoke(main, ["task", "add", "Focus work"])

    result = runner.invoke(main, ["timer", "start", "1"])
    assert result.exit_code == 0
    assert "Started session" in result.output

    result = runner.invoke(main, ["timer", "status"])
    assert "Running" in result.output

    result = runner.invoke(main, ["timer", "stop", "--note", "made progress"])
    assert result.exit_code == 0
    assert "Stopped session" in result.output

    result = runner.invoke(main, ["timer", "status"])
    assert "No session currently running" in result.output


def test_cannot_start_two_sessions_at_once(runner, cli_env):
    runner.invoke(main, ["task", "add", "Task A"])
    runner.invoke(main, ["task", "add", "Task B"])

    runner.invoke(main, ["timer", "start", "1"])
    result = runner.invoke(main, ["timer", "start", "2"])
    assert "already running" in result.output


def test_stop_with_no_active_session(runner, cli_env):
    result = runner.invoke(main, ["timer", "stop"])
    assert "No session is currently running" in result.output


def test_start_timer_on_missing_task(runner, cli_env):
    result = runner.invoke(main, ["timer", "start", "42"])
    assert "not found" in result.output
    assert result.exit_code == 1
