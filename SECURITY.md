# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in TraceX, please report it responsibly.

### How to Report

1. **Do NOT** create a public GitHub issue
2. Email: security@tracex.io
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes (optional)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Assessment**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 24-72 hours
  - High: 1-2 weeks
  - Medium: 2-4 weeks
  - Low: Next release

## Security Best Practices

When deploying TraceX:

### Authentication

- [ ] Change default `TRACEX_SECRET_KEY`
- [ ] Use strong, unique passwords for PostgreSQL
- [ ] Enable TLS for all connections
- [ ] Rotate API keys regularly

### Network Security

- [ ] Don't expose PostgreSQL directly
- [ ] Use firewall rules
- [ ] Configure CORS properly
- [ ] Enable rate limiting

### Data Protection

- [ ] Set up regular backups
- [ ] Configure data retention policies
- [ ] Encrypt sensitive evidence
- [ ] Audit access logs regularly

### Environment Variables

Never commit these to version control:
- `TRACEX_SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `TELEGRAM_BOT_TOKEN`
- `GITHUB_TOKEN`

## Responsible Use

TraceX is designed for:
- Security research
- Bug bounty hunting
- Threat intelligence
- Digital forensics
- Legitimate investigations

### Prohibited Uses

Do NOT use TraceX to:
- Access unauthorized systems
- Harvest private personal data
- Bypass security controls
- Conduct offensive operations
- Violate terms of service

## Compliance

TraceX implements:
- Data encryption at rest
- Secure password hashing (bcrypt)
- API key hashing
- Audit logging
- Configurable data retention
- GDPR-ready data deletion

## Updates

Security patches are released as:
- Patch versions for critical fixes
- Mentioned in changelog
- Announced on Discord

## Contact

- Security issues: security@tracex.io
- General inquiries: contact@tracex.io
- Bug reports: GitHub Issues

PGP Key available on request for sensitive communications.
