"""TraceX CLI URL command."""

import asyncio

import httpx
import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="URL intelligence collection")
console = Console()


@app.command("lookup")
def lookup(
    url: str = typer.Argument(..., help="URL to investigate"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    api_url: str = typer.Option("http://localhost:8000", "--api", help="API URL"),
):
    """Look up URL intelligence."""
    console.print(f"[cyan]Analyzing URL:[/cyan] {url}")

    async def _lookup():
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{api_url}/api/v1/lookup",
                    json={"target": url, "target_type": "url"},
                )
                data = response.json()

                if json_output:
                    console.print_json(data)
                else:
                    console.print()
                    summary = f"""[bold]URL:[/bold] {data.get('url', url)}
[bold]Status:[/bold] {data.get('http', {}).get('status_code', 'N/A')}
[bold]Title:[/bold] {data.get('http', {}).get('page_title', 'N/A')}
[bold]Response Time:[/bold] {data.get('http', {}).get('response_time_ms', 'N/A')}ms"""

                    console.print(Panel(summary, title="[cyan]URL Intelligence[/cyan]", border_style="cyan"))

            except httpx.ConnectError:
                console.print("[red]Error:[/red] Cannot connect to API. Is it running?")
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

    asyncio.run(_lookup())


if __name__ == "__main__":
    app()
