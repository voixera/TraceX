"""TraceX CLI main application."""

import typer
from rich.console import Console

from apps.cli.commands.case import app as case_cmd
from apps.cli.commands.config import app as config_cmd
from apps.cli.commands.domain import app as domain_cmd
from apps.cli.commands.github import app as github_cmd
from apps.cli.commands.graph import app as graph_cmd
from apps.cli.commands.report import app as report_cmd
from apps.cli.commands.url import app as url_cmd
from apps.cli.commands.username import app as username_cmd

app = typer.Typer(
    name="tracex",
    help="TraceX — Open-Source OSINT Intelligence Platform",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=True,
)

console = Console()


def version_callback(value: bool):
    if value:
        console.print("[bold cyan]TraceX[/bold cyan] v0.1.0")
        console.print("Open-Source OSINT Intelligence Platform")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output as JSON"
    ),
    api_url: str = typer.Option(
        None, "--api", help="API URL", envvar="TRACEX_API_URL"
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
):
    """TraceX — Open-Source OSINT Intelligence Platform"""
    from packages.common.settings import settings
    settings.debug = debug
    if api_url:
        import os
        os.environ["TRACEX_API_URL"] = api_url


# Register commands
app.add_typer(domain_cmd, name="domain", help="Domain intelligence")
app.add_typer(url_cmd, name="url", help="URL intelligence")
app.add_typer(github_cmd, name="github", help="GitHub intelligence")
app.add_typer(username_cmd, name="username", help="Username intelligence")
app.add_typer(case_cmd, name="case", help="Manage investigation cases")
app.add_typer(report_cmd, name="report", help="Generate reports")
app.add_typer(graph_cmd, name="graph", help="View relationship graph")
app.add_typer(config_cmd, name="config", help="Configure TraceX")


if __name__ == "__main__":
    app()
