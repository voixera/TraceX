"""TraceX CLI graph command."""

import asyncio
import os

import httpx
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="View relationship graph")
console = Console()


def get_api_url() -> str:
    return os.getenv("TRACEX_API_URL", "http://localhost:8000")


@app.command("show")
def show_graph(
    case_id: str = typer.Argument(..., help="Case ID"),
    output: str = typer.Option("", "--output", "-o", help="Save graph data to file"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show relationship graph for a case."""
    console.print(f"[cyan]Loading graph for case:[/cyan] {case_id}")

    async def _show():
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(f"{get_api_url()}/api/v1/graph/{case_id}")
                data = response.json()

                if output:
                    with open(output, "w") as f:
                        import json
                        json.dump(data, f, indent=2)
                    console.print(f"[green]✓[/green] Graph saved to {output}")
                    return

                if json_output:
                    console.print_json(data)
                else:
                    nodes = data.get("nodes", [])
                    edges = data.get("edges", [])

                    console.print()
                    table = Table(title=f"Graph Summary ({len(nodes)} entities, {len(edges)} relationships)", box=None)
                    table.add_column("Type", style="cyan")
                    table.add_column("Count", style="white")

                    type_counts = {}
                    for n in nodes:
                        t = n.get("type", "unknown")
                        type_counts[t] = type_counts.get(t, 0) + 1

                    for t, c in type_counts.items():
                        table.add_row(t, str(c))

                    console.print(table)

            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

    asyncio.run(_show())


if __name__ == "__main__":
    app()
