#!/usr/bin/env python
"""Initialize TraceX database."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.common.logging import setup_logging
from packages.common.settings import settings
from packages.database.session import create_tables, drop_tables, init_database


async def init():
    """Initialize the database."""
    setup_logging(debug=True)

    print("TraceX Database Initialization")
    print("=" * 40)
    print(f"Database URL: {settings.database_url}")
    print()

    if "--reset" in sys.argv:
        confirm = input("This will DROP all existing tables. Continue? (yes/no): ")
        if confirm.lower() == "yes":
            print("Dropping existing tables...")
            init_database(settings.database_url)
            await drop_tables()
            print("✓ Tables dropped")

    print("Creating database tables...")
    init_database(settings.database_url)
    await create_tables()
    print("✓ Tables created")

    print()
    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init())
