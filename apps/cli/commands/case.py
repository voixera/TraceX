"""TraceX CLI case management command."""

import asyncio

import httpx
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(help="Manage investigation cases")
console = Console()


def get_api_url() -> str:
    import os
    return os.getenv("TRACEX_API_URL", "http://localhost:8000")


@app.command("list")
def list_cases(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all investigation cases."""
    console.print("[cyan]Loading cases...[/cyan]")

    async def _list():
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(f"{get_api_url()}/api/v1/cases")
                cases = response.json()

                if json_output:
                    console.print_json(cases)
                else:
                    if not cases:
                        console.print("[yellow]No cases found[/yellow]")
                        return

                    table = Table(title="Investigation Cases", box=None)
                    table.add_column("ID", style="cyan")
                    table.add_column("Name", style="white")
                    table.add_column("Status", style="green")
                    table.add_column("Created", style="blue")

                    for case in cases:
                        table.add_row(
                            case.get("id", "")[:8] + "...",
                            case.get("name", ""),
                            case.get("status", ""),
                            case.get("created_at", "")[:10],
                        )

                    console.print(table)

            except httpx.ConnectError:
                console.print("[red]Error:[/red] Cannot connect to API. Is it running?")
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

    asyncio.run(_list())


@app.command("create")
def create_case(
    name: str = typer.Argument(..., help="Case name"),
    description: str = typer.Option("", "--description", "-d", help="Case description"),
    tags: str = typer.Option("", "--tags", "-t", help="Comma-separated tags"),
):
    """Create a new investigation case."""
    console.print(f"[cyan]Creating case:[/cyan] {name}")

    async def _create():
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                data = {"name": name, "description": description}
                if tags:
                    data["tags"] = [t.strip() for t in tags.split(",")]

                response = await client.post(f"{get_api_url()}/api/v1/cases", json=data)
                case = response.json()
                console.print(f"[green]✓[/green] Case created: {case['id']}")
                console.print(f"  [cyan]Name:[/cyan] {case['name']}")
                console.print(f"  [cyan]Status:[/cyan] {case['status']}")

            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

    asyncio.run(_create())


@app.command("show")
def show_case(
    case_id: str = typer.Argument(..., help="Case ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show case details."""
    async def _show():
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(f"{get_api_url()}/api/v1/cases/{case_id}")
                case = response.json()

                if json_output:
                    console.print_json(case)
                else:
                    targets_response = await client.get(f"{get_api_url()}/api/v1/targets/case/{case_id}")
                    targets = targets_response.json()

                    summary = f"""[bold]ID:[/bold] {case['id']}
[bold]Name:[/bold] {case['name']}
[bold]Description:[/bold] {case.get('description', 'N/A')}
[bold]Status:[/bold] {case['status']}
[bold]Tags:[/bold] {', '.join(case.get('tags', [])) or 'None'}
[bold]Targets:[/bold] {len(targets)}
[bold]Created:[/bold] {case['created_at'][:10]}"""

                    console.print(Panel(summary, title=f"[cyan]Case: {case['name']}[/cyan]"))

            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

    asyncio.run(_show())


@app.command("delete")
def delete_case(
    case_id: str = typer.Argument(..., help="Case ID"),
    confirm: bool = typer.Option(True, "--yes", "-y", help="Skip confirmation"),
):
    """Delete a case."""
    if not confirm:
        console.print(f"[yellow]This will delete case {case_id}. Continue?[/yellow] (y/N)")
        return

    async def _delete():
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                await client.delete(f"{get_api_url()}/api/v1/cases/{case_id}")
                console.print("[green]✓[/green] Case deleted")

            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

    asyncio.run(_delete())


if __name__ == "__main__":
    app()
