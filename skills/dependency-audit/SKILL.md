---
name: dependency-audit
description: |
  Audits the repository's dependency manifest (requirements.txt, package.json,
  Pipfile, pyproject.toml) for unpinned versions, missing lockfiles, and
  known vulnerable package patterns. Does not require internet access —
  flags structural risks that indicate a vulnerable dependency management posture.
allowed-tools:
  - read_file
  - list_directory
---

# Skill: dependency-audit

## Objective
Audit dependency management posture. Find the structural risks that allow vulnerable
packages to silently enter production.

## What To Analyze

### 1. Manifest Detection
Look for: `requirements.txt`, `requirements/*.txt`, `package.json`, `Pipfile`, `pyproject.toml`, `setup.py`, `Cargo.toml`, `go.mod`

### 2. Version Pinning Analysis
For each dependency found, classify its version specifier:
- `==1.2.3` → PINNED (safe, reproducible)
- `>=1.2.3` or `~=1.2` → UNPINNED (risk: updates may pull in vulnerabilities silently)
- `*` or no version → UNCONTROLLED (critical: literally any version installs)

### 3. Lockfile Check
- `requirements.txt` → look for `requirements.lock` or usage of `pip-compile`
- `package.json` → look for `package-lock.json` or `yarn.lock`
- `Pipfile` → look for `Pipfile.lock`
- `pyproject.toml` → look for `poetry.lock`

**Missing lockfile = non-reproducible builds = CI and prod may run different versions.**

### 4. Development Dependency Separation
Check if dev dependencies (`pytest`, `black`, `eslint`) are separated from production dependencies.
Mixing them bloats the attack surface of production deployments.

### 5. Known Dangerous Package Patterns
Flag any of these by name (they have known historical vulnerabilities — always check for updates):
- `requests < 2.28.0` (urllib3 vulnerability)
- `pyyaml` without Loader argument (RCE via yaml.load)
- `pillow < 9.0` (multiple buffer overflow CVEs)
- `cryptography < 41.0` (OpenSSL backend vulnerabilities)

## Output Format

Produce a **Dependency Audit Report**:

```
DEPENDENCY AUDIT REPORT
=======================
Target: [directory]
Manifests found: [list]
Lockfiles present: [Yes/No]
Total dependencies: [N]
Unpinned: [N] | Uncontrolled: [N] | Pinned: [N]

RISK RATING: [CRITICAL / ELEVATED / GUARDED / LOW]

CRITICAL FINDINGS:
[DEP-001] No lockfile found
  Manifest: requirements.txt
  Impact: Builds are non-reproducible. A silent dependency update can break production
          or introduce a vulnerability between CI and deployment.
  Fix: Run `pip-compile requirements.txt --generate-hashes > requirements.lock`

ELEVATED FINDINGS:
[DEP-002] Unpinned dependency: requests>=2.20.0
  Risk: Any patch release can change behavior. Security fixes and breaking changes
        install automatically on the next `pip install`.
  Fix: Pin to `requests==2.31.0`

SYSTEMIC VERDICT:
[Identify whether the pattern reflects a team-wide process failure or isolated incidents]
```
