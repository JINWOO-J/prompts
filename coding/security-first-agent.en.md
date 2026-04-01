---
category: coding
type: prompt
tags:
- agent
- security
- defi
- rule
role: Security Engineer
origin: custom
source: 'https://github.com/josix/awesome-claude-md/blob/main/scenarios/complex-projects/Citadel-Protocol_contracts/analysis.md'
---
# Security-First Agent Rules — Rules for Security-Critical AI Agents

> Rules that AI coding agents must follow in security-critical projects (DeFi, finance, infrastructure, etc.). Extracted from CLAUDE.md patterns in projects like Citadel Protocol.

---

## Prompt

```markdown
## Security Rules

- NEVER hardcode secrets, API keys, or credentials
- NEVER log sensitive data (PII, tokens, passwords)
- ALWAYS validate external input before processing
- ALWAYS use parameterized queries for database access
- NEVER modify auth middleware without explicit approval
- NEVER disable security headers or CORS restrictions
- NEVER expose internal error details to external callers
- ALWAYS use vetted libraries for cryptographic operations
- ALWAYS apply least-privilege principle to new dependencies
- Flag any change to authentication, authorization, or session logic for manual review
```

---

## Usage

Copy the content of the Prompt block above into the Security section of your CLAUDE.md. This is suitable as an agent ruleset for projects where security is the top priority — DeFi, finance, infrastructure, and similar domains.

## Verification

If these rules are working:
- Hardcoded secrets do not appear in commits.
- The agent explicitly requests manual review when modifying auth/authorization logic.
- Tokens, passwords, and PII do not appear in log output.
- When adding new dependencies, the agent mentions the need for a security audit.
