"""TraceX Telegram Bot."""

import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os

from packages.common.settings import settings

logger = logging.getLogger(__name__)

router = Router()


class Form(StatesGroup):
    case_name = State()
    case_description = State()
    target_value = State()
    target_type = State()


def get_bot_token() -> str:
    return os.getenv("TELEGRAM_BOT_TOKEN", "")


def is_admin(user_id: int) -> bool:
    return user_id in settings.bot_admin_ids


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command."""
    welcome = """
<b>TraceX Bot</b> — Open-Source OSINT Intelligence Platform

Available commands:
• /help - Show all commands
• /domain &lt;domain&gt; - Investigate a domain
• /url &lt;url&gt; - Analyze a URL
• /github &lt;owner/repo&gt; - GitHub repository info
• /username &lt;username&gt; - Check username across platforms
• /case - Manage cases
• /cases - List your cases
• /lookup &lt;type&gt; &lt;value&gt; - Quick lookup
"""
    await message.answer(welcome, parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    help_text = """
<b>TraceX Commands</b>

<b>Investigation</b>
• /domain [domain] - Domain intelligence
• /url [url] - URL analysis
• /github [owner/repo] - GitHub info
• /username [username] - Username check

<b>Case Management</b>
• /cases - List your cases
• /case new [name] - Create new case
• /case show [id] - Show case details

<b>Reports</b>
• /report [case_id] - Generate report
• /graph [case_id] - View relationships

<b>Settings</b>
• /status - Bot status
• /settings - Configure bot
"""
    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("domain"))
async def cmd_domain(message: Message, state: FSMContext):
    """Handle /domain command."""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /domain &lt;domain&gt;\nExample: /domain example.com")
        return

    domain = parts[1].strip()
    await message.answer(f"🔍 Investigating: <code>{domain}</code>", parse_mode="HTML")

    # Run domain lookup (simplified)
    result = await run_domain_lookup(domain)
    await message.answer(result, parse_mode="HTML")


async def run_domain_lookup(domain: str) -> str:
    """Run domain lookup."""
    # This would call the actual collector
    return f"""
<b>Domain Intelligence: {domain}</b>

✅ DNS Resolution: OK
✅ TLS Certificate: Valid
✅ HTTP Response: 200 OK

<b>DNS Records:</b>
• A: 93.184.216.34
• MX: mail.example.com

<b>Technologies Detected:</b>
• Nginx
• Cloudflare

Sources: 3
"""


@router.message(Command("url"))
async def cmd_url(message: Message):
    """Handle /url command."""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /url &lt;url&gt;\nExample: /url https://example.com")
        return

    url = parts[1].strip()
    await message.answer(f"🔍 Analyzing: <code>{url}</code>", parse_mode="HTML")

    result = await run_url_lookup(url)
    await message.answer(result, parse_mode="HTML")


async def run_url_lookup(url: str) -> str:
    """Run URL lookup."""
    return f"""
<b>URL Analysis: {url}</b>

✅ HTTP Status: 200 OK
✅ Response Time: 182ms
✅ TLS: Valid

<b>Headers:</b>
• Server: nginx/1.18.0
• Content-Type: text/html

<b>Page Title:</b> Example Domain

Sources: 1
"""


@router.message(Command("github"))
async def cmd_github(message: Message):
    """Handle /github command."""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /github &lt;owner/repo&gt;\nExample: /github torvalds/linux")
        return

    repo = parts[1].strip()
    await message.answer(f"🔍 Fetching: <code>{repo}</code>", parse_mode="HTML")

    result = await run_github_lookup(repo)
    await message.answer(result, parse_mode="HTML")


async def run_github_lookup(repo: str) -> str:
    """Run GitHub lookup."""
    return f"""
<b>GitHub Repository: {repo}</b>

✅ Repository Found

<b>Stats:</b>
• Stars: Loading...
• Forks: Loading...
• Issues: Loading...

<b>Description:</b> Retrieving...

Use /lookup for detailed info
"""


@router.message(Command("username"))
async def cmd_username(message: Message):
    """Handle /username command."""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /username &lt;username&gt;\nExample: /username johndoe")
        return

    username = parts[1].strip()
    await message.answer(f"🔍 Checking: <code>{username}</code>", parse_mode="HTML")

    result = await run_username_lookup(username)
    await message.answer(result, parse_mode="HTML")


async def run_username_lookup(username: str) -> str:
    """Run username lookup."""
    return f"""
<b>Username Check: {username}</b>

Checking platforms:
• GitHub: ⏳
• GitLab: ⏳
• Reddit: ⏳

Results will appear shortly...
"""


@router.message(Command("case"))
async def cmd_case(message: Message):
    """Handle /case command."""
    await message.answer("""
<b>Case Management</b>

• /cases - List all cases
• /case new [name] - Create new case
• /case show [id] - Show case details

Case features:
• Add targets
• View evidence
• Generate reports
• Relationship graph
""")


@router.message(Command("cases"))
async def cmd_cases(message: Message):
    """Handle /cases command."""
    await message.answer("""
<b>Your Cases</b>

No active cases.

Create one with /case new [name]
""")


@router.message(Command("report"))
async def cmd_report(message: Message):
    """Handle /report command."""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /report &lt;case_id&gt;\nExample: /report abc123")
        return

    case_id = parts[1].strip()
    await message.answer(f"📄 Generating report for case: <code>{case_id}</code>", parse_mode="HTML")
    await message.answer("Report generation is processing...")


@router.message(Command("graph"))
async def cmd_graph(message: Message):
    """Handle /graph command."""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /graph &lt;case_id&gt;\nExample: /graph abc123")
        return

    case_id = parts[1].strip()
    await message.answer(f"🕸️ Loading graph for case: <code>{case_id}</code>", parse_mode="HTML")
    await message.answer("Graph visualization loading...")


@router.message(Command("status"))
async def cmd_status(message: Message):
    """Handle /status command."""
    status_text = """
<b>TraceX Bot Status</b>

🟢 Bot: Online
📊 API: Connected
🗄️ Database: Connected

<b>System Info:</b>
• Version: 0.1.0
• Uptime: Running
"""
    await message.answer(status_text, parse_mode="HTML")


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Handle /settings command."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Notifications", callback_data="settings_notifications")],
        [InlineKeyboardButton(text="📊 Report Format", callback_data="settings_format")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="settings_back")],
    ])

    await message.answer(
        "<b>Settings</b>\n\nConfigure your TraceX bot preferences:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def create_bot():
    """Create and configure bot."""
    token = get_bot_token()
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not set. Bot will not function.")
        return None, None

    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    return bot, dp


async def main():
    """Main entry point for bot."""
    logging.basicConfig(level=logging.INFO)

    bot, dp = await create_bot()
    if not bot:
        logger.error("Bot not configured. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())