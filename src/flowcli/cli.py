from __future__ import annotations

import click
from rich.console import Console

from flowcli import __version__
from flowcli.commands.report import report
from flowcli.commands.task import task
from flowcli.commands.timer import timer
from flowcli.config import Config
from flowcli.db import Database

console = Console()


@click.group()
@click.version_option(__version__, prog_name="flow")
@click.pass_context
def main(ctx):
    """FlowCLI — a git-aware task and time-tracking CLI for developers.

    Run `flow task add "..."` to create a task, `flow timer start <id>` to
    track time on it, and `flow report` to see where your time went.
    """
    ctx.ensure_object(dict)
    config = Config.load()
    ctx.obj["config"] = config
    ctx.obj["db"] = Database(config.db_path)


@main.result_callback()
@click.pass_context
def _cleanup(ctx, *_args, **_kwargs):
    db = ctx.obj.get("db")
    if db is not None:
        db.close()


main.add_command(task)
main.add_command(timer)
main.add_command(report)


if __name__ == "__main__":
    main()
