# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.0 (Sprint 2) | Yes |
| 0.1.x (Sprints 0-1) | Yes |
| < 0.1.0 | No |

## Security Principles

This project is built with security as a first-class concern:

1. **No secrets in code** — All secrets are environment-driven via `.env`
2. **UUID primary keys** — Prevents IDOR (Insecure Direct Object Reference) attacks
3. **Soft deletes** — Preserves audit trail for deleted data
4. **Structured logging** — All security-relevant events logged with trace IDs
5. **Open source** — Full code transparency for security review

## Reporting a Vulnerability

We take security vulnerabilities seriously. Please report security
vulnerabilities by emailing **security@neet-compass.example.org** (replace with
actual email) or by opening a private issue on GitHub.

### What to Include

When reporting a vulnerability, please include:

- A clear description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Initial response**: within 24 hours
- **Acknowledgment**: within 48 hours
- **Investigation**: within 3 business days
- **Patch release**: within 7 days for critical, 30 days for non-critical

### Disclosure Policy

- We follow **responsible disclosure** — we do not publish vulnerability details
  until a fix is available
- We will credit reporters (unless they prefer anonymity)
- We will not pursue legal action against researchers who report vulnerabilities
  in good faith

## Security Best Practices for Deployers

### Database

- Use a strong `POSTGRES_PASSWORD` in production (min 32 characters)
- Enable SSL/TLS for database connections in production
- Run PostgreSQL with `sslmode=require`
- Regular backups with encrypted storage
- Apply PostgreSQL security updates promptly

### Application

- Generate a strong `SECRET_KEY` (min 50 characters) for JWT signing
- Set `APP_ENV=production` to disable `/docs` and OpenAPI schema
- Configure CORS origins explicitly (do not use `*`)
- Use HTTPS in production (terminate TLS at the load balancer)
- Set appropriate rate limits for API endpoints

### Environment

- Never commit `.env` files to version control
- Use a secrets manager (HashiCorp Vault, AWS Secrets Manager, etc.)
  in production
- Set restrictive file permissions on configuration files
- Run containers as non-root user
- Keep Docker images updated with security patches

## Dependency Security

- All dependencies are checked for known vulnerabilities in CI
- Use `pip-audit` or `safety` to check for vulnerable dependencies
- Pin dependency versions in `requirements.txt`
- Review new dependencies for security posture before adding

## Code Security Standards

- All user inputs must be validated via Pydantic schemas
- SQL queries must use SQLAlchemy ORM (no raw SQL with user input)
- Never construct SQL queries by string concatenation
- Use proper error handling — never expose stack traces to users
- Log security events (failed auth, invalid inputs, etc.)

## Data Protection

- User passwords are hashed with bcrypt/scrypt (never plaintext)
- PII is stored encrypted at rest in the database
- Soft deletes preserve audit trail
- Users can request data deletion (GDPR Article 17)
- Data retention policies are documented in the project constitution

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [PostgreSQL Security Checklist](https://www.postgresql.org/docs/current/security-checklist.html)
- [PROJECT_CONSTITUTION.md](PROJECT_CONSTITUTION.md) — Security policies
