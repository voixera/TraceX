"""TraceX CLI report generation command."""

import asyncio
import os

import httpx
import typer
from rich.console import Console

app = typer.Typer(help="Generate investigation reports")
console = Console()


def get_api_url() -> str:
    return os.getenv("TRACEX_API_URL", "http://localhost:8000")


@app.command("generate")
def generate(
    case_id: str = typer.Argument(..., help="Case ID"),
    format: str = typer.Option("markdown", "--format", "-f", help="Report format (markdown, json, html)"),
    output: str = typer.Option("", "--output", "-o", help="Output file"),
):
    """Generate a report for a case."""
    console.print(f"[cyan]Generating {format} report for case:[/cyan] {case_id}")

    async def _generate():
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{get_api_url()}/api/v1/reports",
                    json={"case_id": case_id, "format": format},
                )
                report = response.json()

                content = report.get("content", "")
                if output:
                    with open(output, "w") as f:
                        f.write(content)
                    console.print(f"[green]✓[/green] Report saved to {output}")
                else:
                    console.print(content)

            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

    asyncio.run(_generate())


@app.command("list")
def list_reports(
    case_id: str = typer.Argument("", help="Case ID to filter by"),
):
    """List available reports."""
    async def _list():
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                url = f"{get_api_url()}/api/v1/reports"
                if case_id:
                    url += f"?case_id={case_id}"

                response = await client.get(url)
                reports = response.json()

                if reports:
                    from rich.table import Table
                    table = Table(title="Reports", box=None)
                    table.add_column("ID", style="cyan")
                    table.add_column("Title", style="white")
                    table.add_column("Format", style="green")
                    table.add_column("Generated", style="blue")

                    for r in reports:
                        table.add_row(
                            r.get("id", "")[:8] + "...",
                            r.get("title", ""),
                            r.get("format", ""),
                            r.get("generated_at", "")[:10],
                        )

                    console.print(table)
                else:
                    console.print("[yellow]No reports found[/yellow]")

            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

    asyncio.run(_list())


if __name__ == "__main__":
    app()
