from __future__ import annotations

import click
from rich.console import Console

from flowcli.models import duration_seconds, format_duration

console = Console()


@click.group()
def timer():
    """Start and stop time-tracking sessions."""


@timer.command("start")
@click.argument("task_id", type=int)
@click.pass_context
def start(ctx, task_id: int):
    """Start tracking time on a task."""
    db = ctx.obj["db"]

    task = db.get_task(task_id)
    if task is None:
        console.print(f"[red]Task #{task_id} not found.[/red]")
        return

    existing = db.open_session()
    if existing is not None:
        console.print(
            f"[yellow]Session already running for task #{existing['task_id']}. "
            "Stop it first with `flow timer stop`.[/yellow]"
        )
        return

    session_id = db.start_session(task_id)
    console.print(f"[green]Started session #{session_id} on task #{task_id}[/green]: {task['description']}")


@timer.command("stop")
@click.option("--note", "-n", default=None, help="Optional note describing the session.")
@click.pass_context
def stop(ctx, note: str | None):
    """Stop the currently running session."""
    db = ctx.obj["db"]

    session = db.open_session()
    if session is None:
        console.print("[yellow]No session is currently running.[/yellow]")
        return

    db.stop_session(session["id"], note=note)
    updated = db.get_task(session["task_id"])
    stopped = db.sessions_for_report()
    # Find just-stopped session for duration display
    this_session = next((s for s in stopped if s["id"] == session["id"]), None)
    duration_text = ""
    if this_session and this_session["ended_at"]:
        secs = duration_seconds(this_session["started_at"], this_session["ended_at"])
        duration_text = f" ({format_duration(secs)})"

    console.print(
        f"[green]Stopped session #{session['id']}[/green] on task #{session['task_id']}"
        f" ({updated['description']}){duration_text}"
    )


@timer.command("status")
@click.pass_context
def status(ctx):
    """Show the currently running session, if any."""
    db = ctx.obj["db"]
    session = db.open_session()
    if session is None:
        console.print("[dim]No session currently running.[/dim]")
        return

    task = db.get_task(session["task_id"])
    console.print(
        f"[cyan]Running:[/cyan] task #{session['task_id']} ({task['description']}) "
        f"since {session['started_at']}"
    )
