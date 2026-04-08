---
name: compliance-check
description: |
  Audits the repository for standard project infrastructure: LICENSE, README,
  CONTRIBUTING.md, SECURITY.md, .gitignore, CI/CD workflows, and .env.example.
  Also checks for git hygiene issues: committed secrets files, node_modules,
  build artifacts, and merge conflict markers left in code.
  Fast, opinionated, and zero-tolerance for missing basics.
allowed-tools:
  - read_file
  - list_directory
---

# Skill: compliance-check

## Objective
Audit the repository's project infrastructure and git hygiene. A repository missing
basic files is unmaintainable, uncontributable, and signals institutional immaturity.

## Checks to Perform

### Project Infrastructure (Required)
| File | Required | Why |
|------|----------|-----|
| `README.md` | MANDATORY | Entry point — without it, nobody can use the project |
| `LICENSE` | MANDATORY | Without a license, the code is legally All Rights Reserved |
| `.gitignore` | MANDATORY | Without it, secrets, build artifacts, and IDE files get committed |
| `CONTRIBUTING.md` | STRONG | Without it, contributors guess at process |
| `SECURITY.md` | STRONG | Without it, security researchers have no disclosure channel |
| `.env.example` | STRONG | Without it, users don't know what environment variables are needed |
| `requirements.txt` or equivalent | MANDATORY | Without it, nobody can run the project |

### CI/CD Infrastructure
Look for `.github/workflows/`, `.gitlab-ci.yml`, `.circleci/`, `Makefile`, `justfile`.
**No CI/CD = code ships without automated testing.**

### Git Hygiene Issues
Scan for committed files that should never be in a repository:
- `.env` (credentials file)
- `node_modules/` directory
- `__pycache__/` directory
- `*.pyc` compiled files
- `.DS_Store` (macOS directory metadata)
- `dist/`, `build/`, `*.egg-info/` (build artifacts)
- `<<<<<<`, `=======`, `>>>>>>>` (unresolved merge conflicts in code files)

### README Quality Check
If README.md exists, verify it contains:
- Project description (what it does)
- Installation instructions
- Usage/quickstart instructions
- At minimum, a mention of how to configure credentials

## Output Format

Produce a **Compliance Report**:

```
COMPLIANCE REPORT
=================
Target: [directory]
Infrastructure Score: [N/10]

✅ PRESENT:   README.md, .gitignore, requirements.txt
❌ MISSING:   LICENSE, CONTRIBUTING.md, SECURITY.md, .env.example
⚠️  WARNING:  No CI/CD workflows found

GIT HYGIENE:
✅ No node_modules committed
✅ No .env committed  
⚠️  __pycache__/ found — add to .gitignore

README QUALITY: [PASS / INCOMPLETE / MISSING]

SYSTEMIC VERDICT:
[State whether missing infrastructure indicates a junior team, a prototype that shipped
to production, or deliberate technical debt — and what the systemic fix is]
```
