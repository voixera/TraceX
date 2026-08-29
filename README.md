# TraceX — Open-Source OSINT Intelligence Platform

<p align="center">
  <img src="mainlogo.svg" alt="TraceX" width="200" />
</p>

<p align="center">
  Open-source intelligence, without the noise.
</p>

<p align="center">
  <a href="https://github.com/voixera/TraceX/actions/workflows/ci.yml">
    <img src="https://github.com/voixera/TraceX/actions/workflows/ci.yml/badge.svg" alt="CI" />
  </a>
  <a href="https://pypi.org/project/tracex/">
    <img src="https://img.shields.io/pypi/v/tracex.svg" alt="PyPI" />
  </a>
  <a href="https://github.com/voixera/TraceX/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" />
  </a>
  <a href="https://discord.gg/tracex">
    <img src="https://img.shields.io/badge/Discord-TraceX-7289da.svg" alt="Discord" />
  </a>
</p>

---

## Features

- **Multiple Interfaces**: CLI, Telegram Bot, and Web Dashboard
- **Modular Collectors**: Domain, URL, GitHub, Username intelligence
- **Relationship Graph**: Visualize entity connections
- **Case Management**: Organize investigations with evidence tracking
- **Report Generation**: Export findings in JSON, Markdown, HTML
- **Plugin System**: Extend with custom collectors
- **REST API**: Integrate with your workflow

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         TraceX Core                         │
│                  Intelligence Engine                         │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
      CLI                 Telegram              Web
      Client               Bot                 Dashboard
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │    Collectors     │
                    └─────────┬─────────┘
                              │
       ┌──────────┬───────────┼───────────┬──────────┐
       ▼          ▼           ▼           ▼          ▼
    Domain      DNS        GitHub      URL       Username
    Intel       Intel      Intel      Intel      Intel
```

## Quick Start

### Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/voixera/TraceX.git
cd TraceX

# Copy environment file
cp .env.example .env

# Edit .env and add your API keys
# TRACEX_SECRET_KEY=your-secret-key
# TELEGRAM_BOT_TOKEN=your-bot-token
# GITHUB_TOKEN=your-github-token

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/voixera/TraceX.git
cd TraceX

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e ".[dev]"

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python -m packages.database.session

# Run the API
uvicorn apps.api.main:app --reload

# In another terminal, run the CLI
tracex --help
```

## CLI Usage

```bash
# Domain investigation
tracex domain lookup example.com

# GitHub repository intelligence
tracex github lookup torvalds/linux

# Username check across platforms
tracex username lookup johndoe

# Case management
tracex case list
tracex case create "My Investigation"
tracex case show abc123

# Output as JSON
tracex domain lookup example.com --json

# Configure API endpoint
tracex --api http://localhost:8000 domain lookup example.com
```

## Telegram Bot

Start the bot and use these commands:

```
/start - Get started
/help - Show all commands
/domain <domain> - Investigate domain
/url <url> - Analyze URL
/github <owner/repo> - GitHub info
/username <username> - Check username
/cases - List your cases
/report <case_id> - Generate report
```

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/cases` | Create a new case |
| GET | `/cases` | List all cases |
| GET | `/cases/{id}` | Get case details |
| POST | `/targets` | Add target to case |
| POST | `/investigations` | Start investigation |
| GET | `/entities/{id}` | Get entity details |
| GET | `/graph/{case_id}` | Get relationship graph |
| POST | `/reports` | Generate report |

Full API documentation: `http://localhost:8000/docs`

## Web Dashboard

Access at `http://localhost:3000`

Features:
- Dashboard with statistics
- Case management
- Investigation launcher
- Relationship graph visualization
- Evidence browser
- Activity feed
- Settings

## Collectors

### Domain Collector
- DNS records (A, AAAA, MX, TXT, NS, CNAME)
- TLS certificate information
- HTTP response analysis
- Technology detection

### GitHub Collector
- Repository metadata
- Contributors
- Issues and PRs
- Releases
- Topics

### Username Collector
- Platform presence check
- Cross-platform matching

### URL Collector
- HTTP status and headers
- Redirect chain
- robots.txt analysis
- Sitemap discovery

## Configuration

### Rate Limits

```yaml
rate_limits:
  github:
    requests_per_minute: 30
  dns:
    requests_per_second: 5
  default:
    requests_per_minute: 60
```

### Plugin Configuration

Plugins are stored in `plugins/` directory:

```python
from packages.collectors.base import BaseCollector

class MyCollector(BaseCollector):
    name = "my_collector"
    description = "Custom collector"
    target_types = [TargetType.DOMAIN]

    async def _collect_impl(self, context):
        # Your logic here
        pass
```

## Security

- All data is encrypted at rest
- API keys stored securely
- Rate limiting on all endpoints
- Audit logging for compliance
- No sensitive data in logs

See [SECURITY.md](SECURITY.md) for responsible disclosure.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- 📖 [Documentation](https://tracex.readthedocs.io)
- 💬 [Discord](https://discord.gg/tracex)
- 🐛 [Issue Tracker](https://github.com/voixera/TraceX/issues)
- 📧 [Security Reports](security@tracex.io)

---

Built with ❤️ by the security community, for the security community.
