"""TraceX CLI config command."""

import typer
from rich.console import Console
import os
from pathlib import Path
import json

app = typer.Typer(help="Configure TraceX")
console = Console()


CONFIG_PATH = Path.home() / ".tracex" / "config.json"


def get_config():
    if not CONFIG_PATH.exists():
        return {
            "api_url": os.getenv("TRACEX_API_URL", "http://localhost:8000"),
            "telegram_token": "",
            "output_format": "rich",
            "debug": False,
        }
    with open(CONFIG_PATH) as f:
        return json.load(f)


def save_config(config: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


@app.command("show")
def show_config():
    """Show current configuration."""
    config = get_config()
    console.print_json(data=config)


@app.command("set")
def set_config(
    key: str = typer.Argument(..., help="Config key"),
    value: str = typer.Argument(..., help="Config value"),
):
    """Set a configuration value."""
    config = get_config()
    config[key] = value
    save_config(config)
    console.print(f"[green]✓[/green] Set {key} = {value}")


@app.command("get")
def get_config_value(
    key: str = typer.Argument(..., help="Config key"),
):
    """Get a configuration value."""
    config = get_config()
    value = config.get(key, "")
    if value:
        console.print(f"{key} = {value}")
    else:
        console.print(f"[yellow]Key '{key}' not set[/yellow]")


@app.command("reset")
def reset_config(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Reset configuration to defaults."""
    if not confirm:
        console.print("[yellow]Reset all configuration? This will remove your custom settings.[/yellow]")
        console.print("Use --yes to confirm.")
        return

    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()
    console.print("[green]✓[/green] Configuration reset")


if __name__ == "__main__":
    app()