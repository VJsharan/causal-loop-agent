---
name: secret-scanner
description: |
  Deep-scans every file in a repository for hardcoded credentials, API keys,
  tokens, and passwords using a library of known credential patterns.
  Reports findings by severity — CRITICAL for active credentials,
  ELEVATED for suspicious patterns. Masks actual credential values in output.
  Never outputs the actual secret — only its location and classification.
allowed-tools: read-file write-file list-directory run-grep-scan
---

# Skill: secret-scanner

## Objective
Find every hardcoded credential, token, and secret in the target repository.
**MASK all actual credential values in output.** Report location and type, never the value.

## Scan Targets

### CRITICAL Patterns (immediate rotation required)
- Hardcoded passwords: `password = "..."`, `passwd = "..."`, `pwd = "..."`
- API keys: `api_key = "..."`, `apikey = "..."`
- Generic secrets: `secret = "..."`, `SECRET_KEY = "..."`
- AWS Access Keys: pattern `AKIA[A-Z0-9]{16}`
- GitHub tokens: pattern `ghp_[a-zA-Z0-9]{36}`
- Stripe keys: pattern `sk_live_[a-zA-Z0-9]+`
- Private key headers: `BEGIN RSA PRIVATE KEY`, `BEGIN EC PRIVATE KEY`

### ELEVATED Patterns (investigate)
- JWT secrets: `jwt_secret`, `JWT_SECRET`
- Database connection strings containing credentials
- `.env` files committed to the repository
- `*.pem`, `*.p12`, `*.pfx`, `*.key` files

## Output Format

Produce a **Secret Scan Report** with this structure:

```
SECRET-SCAN REPORT
==================
Target: [directory]
Files Scanned: [N]
Secrets Found: [N]

CRITICAL FINDINGS:
[SEC-001] TYPE: Hardcoded API Key
  File: src/auth.py, Line: 12
  Pattern matched: api_key = "sk_live_[REDACTED]"
  Action required: ROTATE IMMEDIATELY. Assume this key is compromised.
  Causal root: No pre-commit secret scanning configured. No engineer review caught this.

ELEVATED FINDINGS:
[SEC-002] TYPE: .env file committed
  File: .env, Line: 1
  Pattern matched: .env file present in repository
  Action required: Remove from git history (git filter-repo), add to .gitignore.

SYSTEMIC VERDICT:
[State whether findings indicate a systemic secret management failure or an isolated incident]
```

**MANDATORY:** End every finding with a "Causal root:" that identifies the systemic process failure, never the individual developer.
