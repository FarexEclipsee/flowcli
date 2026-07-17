from __future__ import annotations

import click
from rich.console import Console

from flowcli.exporters import available_formats, get_exporter
from flowcli.models import session_to_dict

console = Console()


@click.command("report")
@click.option(
    "--format",
    "-f",
    "fmt",
    default="markdown",
    help=f"Output format. Available: {', '.join(available_formats())}",
)
@click.option("--project", "-p", default=None, help="Filter by project.")
@click.option(
    "--since", default=None, help="Only include sessions started after this datetime (YYYY-MM-DD)."
)
@click.option(
    "--output", "-o", type=click.Path(dir_okay=False), default=None, help="Write report to a file."
)
@click.pass_context
def report(ctx, fmt: str, project: str | None, since: str | None, output: str | None):
    """Generate a time-tracking report."""
    db = ctx.obj["db"]

    since_dt = f"{since} 00:00:00" if since else None
    rows = db.sessions_for_report(project=project, since=since_dt)
    sessions = [session_to_dict(row) for row in rows]

    try:
        exporter = get_exporter(fmt)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1)

    rendered = exporter.export(sessions)

    if output:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(rendered)
        console.print(f"[green]Report written to {output}[/green]")
    else:
        console.print(rendered)
