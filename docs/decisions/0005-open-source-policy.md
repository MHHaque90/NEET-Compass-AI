# ADR-005: Open Source Policy

- **Status:** Accepted (Sprint 1)
- **Date:** 2026-08-08
- **Deciders:** Lead Architect, Project Founder, Legal Advisor
- **Category:** Licensing & Policy

## Context

NEET Compass AI is committed to being **free, open-source, self-hostable,
and vendor-lock-in-free**. This means:

1. **License** — must be permissive enough for anyone to use, modify, and
   redistribute, including commercial use
2. **Dependencies** — all must be FOSS (Free and Open Source Software)
3. **No vendor lock-in** — must run entirely on free/open-source tooling
4. **No cloud dependency** — self-hostable on commodity hardware
5. **No paid APIs** — must not depend on paid services or proprietary SDKs
6. **Self-hostable** — a single Docker Compose command should spin up everything

The following licenses were evaluated:

| License | Permissive | Commercial Use | Copyleft | Attribution Required |
|---------|-----------|----------------|----------|---------------------|
| MIT | Yes | Yes | No | Yes |
| Apache 2.0 | Yes | Yes | No | Yes (+ patent grant) |
| GPL v3 | Yes | Yes | Strong | Yes (+ copyleft) |
| AGPL v3 | Yes | Yes | Stronger | Yes (+ network copyleft) |
| BSD-3 | Yes | Yes | No | Yes |
| MPL 2.0 | Yes | Yes | Weak | Yes |

The project also needs to consider dependency compatibility. Most Python
data science libraries use BSD, MIT, or Apache 2.0 licenses. GPL/AGPL
dependencies would constrain the project license.

## Decision

### License Selection

We choose the **MIT License** for the following reasons:

1. **Maximally permissive** — anyone can use, modify, and redistribute
2. **Commercial-friendly** — companies can adopt without legal friction
3. **Compatible with all MIT/BSD/Apache 2.0 dependencies** — no conflicts
4. **No patent grant** — simplifies the license text (vs Apache 2.0)
5. **Widely understood** — minimal legal overhead for contributors

The MIT License requires only attribution (preservation of the copyright
notice and license text). This aligns with the project's goal of being
accessible to the widest possible audience while still protecting contributors
from liability.

### Dependency Policy

All dependencies must comply with the **FOSS Permissive License Policy**:

- **Approved licenses:** MIT, BSD (2-clause, 3-clause), Apache 2.0, ISC,
  Unlicense, CC0-1.0
- **Disallowed licenses:** GPL, AGPL, LGPL (strong copyleft), SSPL, Commons
  Clause, or any license with a "non-commercial" restriction
- **Review process:** Every new dependency must be reviewed by the Lead
  Architect and the license must be verified using `pip-licenses` or
  `yolk3k`

### Vendor Lock-in Policy

The project must run entirely on open-source tools:

- **Database:** PostgreSQL (open source)
- **Application server:** Uvicorn + FastAPI (open source)
- **Container runtime:** Docker (open source, though Docker Desktop is
  proprietary for some platforms — Docker Engine is fully open)
- **Cache:** Redis (open source BSD)
- **ML engines:** Pluggable — default is the `unavailable` engine that
  refuses to fabricate scores
- **Data sources:** Official MCC/state PDF/Excel releases only — no paid APIs

### Contributions Policy

- All contributions are made under the **Developer Certificate of Origin (DCO)**
- Contributors retain copyright to their contributions
- The project copyright is held by the contributors as a collective
- **No CLA (Contributor License Agreement)** is required — DCO is sufficient
- All contributions must pass CI (lint, typecheck, test, license check)

### Attribution Requirements

- Every dependency is listed in `requirements.txt` with its license
- A `NOTICE` file is generated during build listing all dependencies
- The `LICENSE` file contains the MIT license text
- `SECURITY.md` documents the security policy
- `CONTRIBUTING.md` documents the contribution process

## Consequences

### Positive
- Maximum adoption — no legal barriers for individuals or companies
- Compatible with all approved open-source dependencies
- Clear contribution process with DCO
- Self-hostable without any paid services
- No vendor lock-in — can be forked and run anywhere

### Negative
- No copyleft protection — companies can fork and close modifications
  (accepted trade-off for maximum adoption)
- Patent protection is weaker than Apache 2.0 (no explicit patent grant)

### Neutral
- The DCO adds a small overhead to commits (sign-off required)
- License verification must be part of CI (automated with `pre-commit` hooks)

## References

- [LICENSE](../LICENSE) — The MIT License text
- [CONTRIBUTING.md](../CONTRIBUTING.md) — Contribution guidelines
- [SECURITY.md](../SECURITY.md) — Security policy
- [ADR-001: Technology Stack](0001-tech-stack.md)
