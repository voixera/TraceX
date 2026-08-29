#!/usr/bin/env python
"""TraceX startup script."""

import subprocess
import sys


def run_command(cmd: list, description: str) -> bool:
    """Run a shell command."""
    print(f"\n{'='*60}")
    print(f"→ {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    """Main startup function."""
    print("""
╔══════════════════════════════════════════╗
║       TraceX — OSINT Intelligence        ║
║        Open-Source Security Platform     ║
╚══════════════════════════════════════════╝
    """)

    if len(sys.argv) < 2:
        print("Usage: python scripts/run.py [command]")
        print("\nCommands:")
        print("  api        - Start FastAPI server")
        print("  bot        - Start Telegram bot")
        print("  worker     - Start background worker")
        print("  web        - Start web dashboard")
        print("  all        - Start all services")
        print("  init       - Initialize database")
        print("  test       - Run tests")
        print("  install    - Install dependencies")
        return

    command = sys.argv[1]

    if command == "api":
        run_command(
            ["uvicorn", "apps.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            "Starting FastAPI server on http://localhost:8000",
        )

    elif command == "bot":
        run_command(
            ["python", "-m", "apps.bot.main"],
            "Starting Telegram bot",
        )

    elif command == "worker":
        run_command(
            ["python", "-m", "apps.api.worker"],
            "Starting background worker",
        )

    elif command == "web":
        run_command(
            ["cd", "apps/web", "&&", "npm", "run", "dev"],
            "Starting web dashboard on http://localhost:3000",
        )

    elif command == "init":
        run_command(
            ["python", "-c", "from packages.database.session import init_database, create_tables; import asyncio; from packages.common.settings import settings; init_database(settings.database_url); asyncio.run(create_tables())"],
            "Initializing database",
        )

    elif command == "test":
        run_command(
            ["pytest", "tests/", "-v"],
            "Running test suite",
        )

    elif command == "install":
        run_command(
            ["pip", "install", "-e", ".[dev]"],
            "Installing dependencies",
        )

    else:
        print(f"Unknown command: {command}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
