"""TraceX CLI domain command."""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import asyncio
import httpx
from datetime import datetime

app = typer.Typer(help="Domain intelligence collection")
console = Console()


@app.command("lookup")
def lookup(
    domain: str = typer.Argument(..., help="Domain to investigate"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    api_url: str = typer.Option("http://localhost:8000", "--api", help="API URL"),
):
    """Look up domain intelligence."""
    console.print(f"[cyan]Investigating domain:[/cyan] {domain}")

    async def _lookup():
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{api_url}/api/v1/lookup",
                    json={"target": domain, "target_type": "domain"},
                )
                data = response.json()

                if json_output:
                    console.print_json(data)
                else:
                    _print_results(data)

            except httpx.ConnectError:
                console.print("[red]Error:[/red] Cannot connect to API. Is it running?")
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

    asyncio.run(_lookup())


def _print_results(data: dict):
    """Print results in human-readable format."""
    console.print()

    # Summary panel
    summary = f"""[bold]Target:[/bold] {data.get('target', 'N/A')}
[bold]Status:[/bold] {data.get('status', 'unknown')}
[bold]Collected:[/bold] {data.get('collected_at', 'N/A')}"""

    console.print(Panel(summary, title="[cyan]Domain Intelligence[/cyan]", border_style="cyan"))
    console.print()

    # DNS Records
    dns = data.get("dns", {})
    if dns:
        table = Table(title="DNS Records", box=None)
        table.add_column("Type", style="cyan")
        table.add_column("Value", style="white")

        for record_type in ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]:
            records = dns.get(record_type.lower(), [])
            if records:
                for record in records:
                    if isinstance(record, dict):
                        table.add_row(record_type, str(record))
                    else:
                        table.add_row(record_type, str(record))

        console.print(table)
        console.print()

    # TLS Certificate
    tls = data.get("tls", {})
    if tls:
        console.print("[bold cyan]TLS Certificate[/bold cyan]")
        console.print(f"  Issuer: {tls.get('issuer', 'N/A')}")
        console.print(f"  Valid Until: {tls.get('valid_to', 'N/A')}")
        console.print()

    # HTTP Info
    http = data.get("http", {})
    if http:
        console.print("[bold cyan]HTTP Response[/bold cyan]")
        console.print(f"  Status: {http.get('status_code', 'N/A')}")
        console.print(f"  Latency: {http.get('response_time_ms', 'N/A')}ms")
        if http.get("technologies"):
            console.print(f"  Technologies: {', '.join(http.get('technologies', []))}")
        console.print()


@app.command("dns")
def dns_records(
    domain: str = typer.Argument(..., help="Domain to query"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    api_url: str = typer.Option("http://localhost:8000", "--api", help="API URL"),
):
    """Get DNS records for domain."""
    console.print(f"[cyan]Fetching DNS records for:[/cyan] {domain}")

    async def _dns():
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{api_url}/api/v1/collectors/dns",
                    json={"target": domain},
                )
                data = response.json()

                if json_output:
                    console.print_json(data)
                else:
                    table = Table(title="DNS Records", box=None)
                    table.add_column("Type", style="cyan")
                    table.add_column("Priority", style="yellow")
                    table.add_column("Value", style="white")

                    for record_type in ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]:
                        records = data.get(record_type.lower(), [])
                        if records:
                            for record in records:
                                if isinstance(record, dict):
                                    table.add_row(
                                        record_type,
                                        str(record.get("preference", "")),
                                        str(record.get("value", record))
                                    )
                                else:
                                    table.add_row(record_type, "", str(record))

                    console.print(table)
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

    asyncio.run(_dns())


if __name__ == "__main__":
    app()