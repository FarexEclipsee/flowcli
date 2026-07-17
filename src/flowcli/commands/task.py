from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from flowcli import git_utils

console = Console()


@click.group()
def task():
    """Create and manage tasks."""


@task.command("add")
@click.argument("description")
@click.option("--project", "-p", default=None, help="Project name (defaults to git repo name).")
@click.option("--tag", "-t", default=None, help="Free-form tag, e.g. 'bug' or 'feature'.")
@click.pass_context
def add(ctx, description: str, project: str | None, tag: str | None):
    """Add a new task."""
    db = ctx.obj["db"]
    config = ctx.obj["config"]

    branch = git_utils.current_branch()
    resolved_project = project or git_utils.repo_name() or config.default_project

    task_id = db.add_task(description, project=resolved_project, tag=tag, branch=branch)
    console.print(
        f"[green]Added task #{task_id}[/green]: {description}"
        + (f" [dim](project: {resolved_project})[/dim]" if resolved_project else "")
    )


@task.command("list")
@click.option("--status", type=click.Choice(["open", "done", "all"]), default="open")
@click.option("--project", "-p", default=None, help="Filter by project.")
@click.pass_context
def list_tasks(ctx, status: str, project: str | None):
    """List tasks."""
    db = ctx.obj["db"]
    filter_status = None if status == "all" else status
    rows = db.list_tasks(status=filter_status, project=project)

    if not rows:
        console.print("[dim]No tasks found.[/dim]")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", justify="right")
    table.add_column("Description")
    table.add_column("Project")
    table.add_column("Tag")
    table.add_column("Branch")
    table.add_column("Status")
    for row in rows:
        status_style = "green" if row["status"] == "done" else "yellow"
        table.add_row(
            str(row["id"]),
            row["description"],
            row["project"] or "-",
            row["tag"] or "-",
            row["branch"] or "-",
            f"[{status_style}]{row['status']}[/{status_style}]",
        )
    console.print(table)


@task.command("done")
@click.argument("task_id", type=int)
@click.pass_context
def done(ctx, task_id: int):
    """Mark a task as done."""
    db = ctx.obj["db"]
    if db.mark_done(task_id):
        console.print(f"[green]Task #{task_id} marked done.[/green]")
    else:
        console.print(f"[red]Task #{task_id} not found or already done.[/red]")


@task.command("rm")
@click.argument("task_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this task?")
@click.pass_context
def rm(ctx, task_id: int):
    """Delete a task and its tracked sessions."""
    db = ctx.obj["db"]
    if db.delete_task(task_id):
        console.print(f"[green]Task #{task_id} deleted.[/green]")
    else:
        console.print(f"[red]Task #{task_id} not found.[/red]")
