"""TraceX CLI username command."""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import asyncio
import httpx

app = typer.Typer(help="Username intelligence collection")
console = Console()


@app.command("lookup")
def lookup(
    username: str = typer.Argument(..., help="Username to investigate"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    api_url: str = typer.Option("http://localhost:8000", "--api", help="API URL"),
):
    """Look up username across public platforms."""
    console.print(f"[cyan]Checking username:[/cyan] {username}")

    async def _lookup():
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{api_url}/api/v1/lookup",
                    json={"target": username, "target_type": "username"},
                )
                data = response.json()

                if json_output:
                    console.print_json(data)
                else:
                    console.print()
                    results = data.get("results", [])
                    if results:
                        table = Table(title="Platform Matches", box=None)
                        table.add_column("Platform", style="cyan")
                        table.add_column("Found", style="green")
                        table.add_column("URL", style="blue")

                        for r in results:
                            found = "[green]✓[/green]" if r.get("found") else "[red]✗[/red]"
                            table.add_row(r.get("platform", ""), found, r.get("url", ""))

                        console.print(table)
                    else:
                        console.print("[yellow]No platforms found[/yellow]")

            except httpx.ConnectError:
                console.print("[red]Error:[/red] Cannot connect to API. Is it running?")
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

    asyncio.run(_lookup())


if __name__ == "__main__":
    app()