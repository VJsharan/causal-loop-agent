# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes    |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, please describe the vulnerability in a private message to the maintainer via GitHub.

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within 48 hours.

## Scope

**In scope:**
- Secret detection false negatives (CausalLoop missed a real credential)
- Credential exposure in agent output (agent outputs actual secrets instead of masking)
- Path traversal vulnerabilities in file-reading tools

**Out of scope:**
- False positives in secret scanning (report as a regular issue)
- Feature requests

## Security Design Principles

CausalLoop is designed with these security boundaries:
- **Never executes code** found inside the target repository
- **Masks credentials** — findings report the presence of secrets, never their value
- **Reads `.env` of the target repo only for pattern detection**, never for extraction
- **API keys are loaded from environment variables only**, never hardcoded
