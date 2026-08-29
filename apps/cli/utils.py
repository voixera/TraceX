"""TraceX CLI shared utilities."""

import os
import json
import asyncio
import httpx
from typing import Any, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
from rich import box

console = Console()


def get_api_url() -> str:
    """Get API URL from env or default."""
    return os.getenv("TRACEX_API_URL", "http://localhost:8000")


async def call_api(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    params: Optional[Dict] = None,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """Call TraceX API."""
    url = f"{get_api_url()}{endpoint}"
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.request(
            method=method,
            url=url,
            json=data,
            params=params,
        )
        response.raise_for_status()
        return response.json()


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[bold red]✗[/bold red] {message}")


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[bold cyan]ℹ[/bold cyan] {message}")


def print_json(data: Any) -> None:
    """Print data as JSON."""
    console.print_json(data=data)


def print_panel(title: str, content: str, style: str = "cyan") -> None:
    """Print content in a panel."""
    panel = Panel(content, title=title, border_style=style, box=box.ROUNDED)
    console.print(panel)


def create_table(title: str, columns: list) -> Table:
    """Create a styled table."""
    table = Table(title=title, box=box.ROUNDED, show_header=True, header_style="bold cyan")
    for col in columns:
        if isinstance(col, tuple):
            table.add_column(col[0], style=col[1] if len(col) > 1 else "white")
        else:
            table.add_column(col)
    return table


def run_async(coro):
    """Run async function in sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)