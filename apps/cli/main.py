"""TraceX CLI main application."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from apps.cli.commands import (
    domain_cmd,
    url_cmd,
    github_cmd,
    username_cmd,
    case_cmd,
    report_cmd,
    graph_cmd,
    config_cmd,
)

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
app.add_typer(domain_cmd.app, name="domain", help="Domain intelligence")
app.add_typer(url_cmd.app, name="url", help="URL intelligence")
app.add_typer(github_cmd.app, name="github", help="GitHub intelligence")
app.add_typer(username_cmd.app, name="username", help="Username intelligence")
app.add_typer(case_cmd.app, name="case", help="Manage investigation cases")
app.add_typer(report_cmd.app, name="report", help="Generate reports")
app.add_typer(graph_cmd.app, name="graph", help="View relationship graph")
app.add_typer(config_cmd.app, name="config", help="Configure TraceX")


if __name__ == "__main__":
    app()