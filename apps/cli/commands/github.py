"""TraceX CLI GitHub command."""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import asyncio
import httpx

app = typer.Typer(help="GitHub intelligence collection")
console = Console()


@app.command("lookup")
def lookup(
    repo: str = typer.Argument(..., help="GitHub repository (owner/repo or URL)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    api_url: str = typer.Option("http://localhost:8000", "--api", help="API URL"),
):
    """Look up GitHub repository intelligence."""
    console.print(f"[cyan]Analyzing repository:[/cyan] {repo}")

    async def _lookup():
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{api_url}/api/v1/lookup",
                    json={"target": repo, "target_type": "github"},
                )
                data = response.json()

                if json_output:
                    console.print_json(data)
                else:
                    console.print()
                    _print_repo(data)

            except httpx.ConnectError:
                console.print("[red]Error:[/red] Cannot connect to API. Is it running?")
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

    asyncio.run(_lookup())


def _print_repo(data: dict):
    """Print repository data."""
    info = data.get("repository", {})
    summary = f"""[bold]Name:[/bold] {info.get('full_name', 'N/A')}
[bold]Description:[/bold] {info.get('description', 'N/A')}
[bold]Language:[/bold] {info.get('language', 'N/A')}
[bold]Stars:[/bold] {info.get('stargazers_count', 0):,}
[bold]Forks:[/bold] {info.get('forks_count', 0):,}
[bold]Open Issues:[/bold] {info.get('open_issues_count', 0):,}"""

    console.print(Panel(summary, title="[cyan]Repository Information[/cyan]", border_style="cyan"))
    console.print()

    contributors = data.get("contributors", [])
    if contributors:
        table = Table(title="Top Contributors", box=None)
        table.add_column("Username", style="cyan")
        table.add_column("Contributions", style="green")

        for c in contributors[:10]:
            table.add_row(c.get("login", ""), str(c.get("contributions", 0)))

        console.print(table)


if __name__ == "__main__":
    app()