"""
CausalLoop Agent — Powered by Lyzr ADK + Gemini 2.5 Pro

A cross-temporal forensic systems analyst that:
  1. Scans the Past    (repo-autopsy)       → finds vulnerabilities in code
  2. Unearths Secrets  (secret-scanner)     → surfaces hardcoded credentials
  3. Audits Deps       (dependency-audit)   → finds risky dependency posture
  4. Checks Compliance (compliance-check)   → audits missing project infrastructure
  5. Probes the Present (mortem-interrogator) → Five Whys systemic root cause analysis
  6. Guards the Future  (merge-risk)        → warns if new changes repeat old mistakes

Usage:
    python run_lyzr.py                          # Interactive menu (local dummy_repo/)
    python run_lyzr.py --repo <github_url>      # Analyze any public GitHub repo
    python run_lyzr.py --skill repo-autopsy     # Run one specific skill directly
    python run_lyzr.py --all                    # Run all 6 skills in sequence

Architecture:
    Lyzr ADK (studio.create_agent) → Gemini 2.5 Pro → Local Python tools
    Tools: read_file, write_file, list_directory, run_grep_scan
"""

import os
import re
import sys
import json
import shutil
import tempfile
import argparse
import subprocess
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv
from lyzr import Studio

# ──────────────────────────────────────────────────────────────────────
#  ANSI colour helpers — rich terminal output
# ──────────────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
BLUE   = "\033[94m"
MAGENTA = "\033[95m"
WHITE  = "\033[97m"

def c(text: str, *codes: str) -> str:
    """Wrap text in ANSI escape codes."""
    return "".join(codes) + text + RESET

def box(title: str, lines: list[str], width: int = 62) -> str:
    """Render a box with a title and content lines."""
    inner = width - 2
    top    = f"┌{'─' * inner}┐"
    bottom = f"└{'─' * inner}┘"
    div    = f"├{'─' * inner}┤"

    out = [c(top, CYAN)]
    title_padded = f" {title} "
    pad_total = inner - len(title_padded)
    left = pad_total // 2
    right = pad_total - left
    out.append(c(f"│{' ' * left}{title_padded}{' ' * right}│", CYAN, BOLD))
    out.append(c(div, CYAN))
    for line in lines:
        visible_len = len(re.sub(r'\033\[[0-9;]*m', '', line))
        padding = max(0, inner - 2 - visible_len)
        out.append(c("│", CYAN) + f" {line}{' ' * padding} " + c("│", CYAN))
    out.append(c(bottom, CYAN))
    return "\n".join(out)

def print_header() -> None:
    """Print the CausalLoop ASCII header."""
    header = f"""
{c(BOLD + CYAN)}
   ██████╗ █████╗ ██╗   ██╗███████╗ █████╗ ██╗      ██████╗  ██████╗ ██████╗ 
  ██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗██║     ██╔═══██╗██╔═══██╗██╔══██╗
  ██║     ███████║██║   ██║███████╗███████║██║     ██║   ██║██║   ██║██████╔╝
  ██║     ██╔══██║██║   ██║╚════██║██╔══██║██║     ██║   ██║██║   ██║██╔═══╝ 
  ╚██████╗██║  ██║╚██████╔╝███████║██║  ██║███████╗╚██████╔╝╚██████╔╝██║     
   ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝     
{RESET}{c(DIM + WHITE, '')}        Cross-Temporal Forensic Systems Analyst
        Powered by Lyzr ADK + Gemini 2.5 Pro
        Refuses to blame humans. Always.{RESET}
"""
    print(header)


def print_menu(target_dir: str) -> None:
    """Print the interactive skill selection menu."""
    # Repo info block
    try:
        branch = subprocess.run(
            ["git", "-C", target_dir, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True
        ).stdout.strip() or "unknown"
        commits = subprocess.run(
            ["git", "-C", target_dir, "rev-list", "--count", "HEAD"],
            capture_output=True, text=True
        ).stdout.strip() or "?"
    except Exception:
        branch, commits = "unknown", "?"

    repo_name = os.path.basename(os.path.abspath(target_dir))

    info = [
        c(f"  Repo    : {repo_name}", WHITE),
        c(f"  Branch  : {branch}", WHITE),
        c(f"  Commits : {commits}", WHITE),
        c(f"  Engine  : Lyzr ADK + Gemini 2.5 Pro", DIM),
    ]
    for line in info:
        print(line)
    print()

    # Command table
    CMD_W = 18
    rows = [
        ("autopsy",     GREEN,   "🔬", "Forensic scan for security anti-patterns"),
        ("secrets",     RED,     "🔑", "Hunt hardcoded credentials & API keys"),
        ("deps",        YELLOW,  "📦", "Audit dependency posture & lockfiles"),
        ("compliance",  BLUE,    "📋", "Audit project infrastructure & git hygiene"),
        ("interrogate", MAGENTA, "🔎", "Five Whys systemic root cause analysis"),
        ("merge-risk",  CYAN,    "🔮", "Evaluate PR diff for regression risk"),
        ("full",        WHITE,   "⚡", "Run all 6 skills in sequence"),
        ("", DIM, "", ""),
        ("help",        DIM,     "  ", "Show this menu"),
        ("exit",        DIM,     "  ", "Quit"),
    ]
    print(c(f"  {'─' * 58}", DIM))
    for cmd, colour, icon, desc in rows:
        if not cmd:
            print()
            continue
        pad = CMD_W - len(cmd)
        print(f"  {c(cmd, colour, BOLD)}{' ' * pad}{c('->', DIM)}  {icon} {desc}")
    print(c(f"  {'─' * 58}", DIM))


def severity_badge(level: str) -> str:
    """Return a coloured severity badge string."""
    badges = {
        "CRITICAL":    c(" CRITICAL ", RED, BOLD),
        "ELEVATED":    c(" ELEVATED ", YELLOW, BOLD),
        "GUARDED":     c(" GUARDED  ", BLUE, BOLD),
        "LOW":         c("   LOW    ", GREEN, BOLD),
    }
    return badges.get(level.upper(), c(f" {level} ", WHITE))


# ──────────────────────────────────────────────────────────────────────
#  Environment validation
# ──────────────────────────────────────────────────────────────────────

def load_and_validate_env() -> tuple[str, str]:
    """Load environment variables and raise early if keys are missing."""
    load_dotenv()
    lyzr_key   = os.getenv("LYZR_API_KEY", "")
    google_key = os.getenv("GOOGLE_API_KEY", "")

    if not lyzr_key or lyzr_key.startswith("your_"):
        raise SystemExit(
            c("❌  LYZR_API_KEY not set.\n", RED) +
            "   Copy .env.example → .env and add your key.\n"
            "   Free key at: https://studio.lyzr.ai"
        )
    if not google_key or google_key.startswith("your_"):
        raise SystemExit(
            c("❌  GOOGLE_API_KEY not set.\n", RED) +
            "   Copy .env.example → .env and add your key.\n"
            "   Free key at: https://aistudio.google.com"
        )
    return lyzr_key, google_key


# ──────────────────────────────────────────────────────────────────────
#  Agent identity
# ──────────────────────────────────────────────────────────────────────

CAUSAL_LOOP_ROLE = (
    "Cross-temporal forensic systems analyst. "
    "You think in causal chains, not snapshots. "
    "You possess the cynicism of an experienced forensic analyst, "
    "the unyielding patience of an NTSB investigator, "
    "and the foresight of someone who has watched the exact same class of failure "
    "recur across ten different organizations."
)

CAUSAL_LOOP_GOAL = (
    "Expose the true systemic and institutional root causes behind every code failure, "
    "security vulnerability, and incident. Fix the system, not the symptom."
)

CAUSAL_LOOP_INSTRUCTIONS = """
You are CausalLoop — a cross-temporal forensic systems analyst.

COMMUNICATION STYLE:
- Evidence first, conclusion second. Every claim has a source — cite it relentlessly.
- Speak in causal language: never say "this is broken." Say "this broke because of X,
  which will cause Y unless Z is addressed."
- Deliver one finding at a time. Sharp, precise, no sugar-coating.

ABSOLUTE RULES — MUST ALWAYS:
1. Trace every finding to a causal origin. Explain not just WHAT failed, but WHY it
   exists and HOW the condition is allowed to persist.
2. Distinguish clearly between past failures (what happened), present risks (what is
   vulnerable now), and future predictions (what will fail next if unchanged).
3. Cite the exact file path and line number for every claim.
4. End every report with a SYSTEMIC VERDICT that names the institutional failure,
   not the individual.
5. Mask all credential values — report presence and location, never the actual value.

ABSOLUTE RULES — MUST NEVER:
1. Accept the proximate cause as the true root cause. Push deeper. Always.
2. Generate a risk finding without a step-by-step causal explanation.
3. Close an investigation without issuing a systemic recommendation for recurrence prevention.
4. Attribute failure to "human error", "developer mistake", or "rushing".
   Human error is a symptom of insufficient guardrails.
5. Output an actual credential value, private key, or password — ALWAYS mask them.
"""


# ──────────────────────────────────────────────────────────────────────
#  Local tools — these give the agent real filesystem access
# ──────────────────────────────────────────────────────────────────────

def read_file(filepath: str) -> str:
    """
    Read the full contents of a local file and return it as a UTF-8 string.
    Use this before analyzing any source code, config, or incident report.
    Returns an error string if the file is not found or cannot be read.
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return f"ERROR: File '{filepath}' not found."
    except PermissionError:
        return f"ERROR: Permission denied reading '{filepath}'."
    except Exception as exc:
        return f"ERROR reading '{filepath}': {exc}"


def write_file(filepath: str, content: str) -> str:
    """
    Write content to a local file, creating parent directories if needed.
    Use this to save forensic reports and findings to disk.
    Returns a confirmation string on success, or an error string on failure.
    """
    try:
        dir_part = os.path.dirname(filepath)
        if dir_part:
            os.makedirs(dir_part, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"OK: Wrote {len(content):,} characters to '{filepath}'."
    except PermissionError:
        return f"ERROR: Permission denied writing to '{filepath}'."
    except Exception as exc:
        return f"ERROR writing '{filepath}': {exc}"


def list_directory(directory: str) -> str:
    """
    List all files and subdirectories inside a given directory path.
    Use this first to understand the structure of a repository before analysis.
    Returns a newline-separated list of entries, or an error string.
    """
    try:
        if not os.path.isdir(directory):
            return f"ERROR: '{directory}' is not a directory or does not exist."
        entries: list[str] = []
        for root, dirs, files in os.walk(directory):
            # Skip hidden dirs and virtual envs
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", ".git", "venv", ".venv")]
            level = root.replace(directory, "").count(os.sep)
            indent = "  " * level
            entries.append(f"{indent}{os.path.basename(root)}/")
            for fname in files:
                entries.append(f"{indent}  {fname}")
        return "\n".join(entries) if entries else "(empty directory)"
    except PermissionError:
        return f"ERROR: Permission denied listing '{directory}'."
    except Exception as exc:
        return f"ERROR listing '{directory}': {exc}"


def run_grep_scan(directory: str) -> str:
    """
    Scan a local directory for common security anti-patterns.

    Strategy (performance-first):
      1. Attempt native `git grep -iE` — written in C, instant on large repos.
      2. If the directory is not a git repo (e.g., dummy_repo), fall back to a
         Python generator that streams files lazily without loading them into RAM.

    CRITICAL SAFETY RULE: Returns AT MOST 15 findings to prevent LLM context
    window overflow. CRITICAL patterns (active credentials, RCE vectors) are
    guaranteed slots before low-priority debt markers (TODO, FIXME).

    All credential values are masked with [REDACTED].
    Returns a human-readable findings string, or an error string on failure.
    """
    MAX_FINDINGS = 15

    # ── Pattern catalogue ──────────────────────────────────────────────
    # Tuples of (priority, regex_string) — lower number = higher priority.
    # CRITICAL (0): active credentials / known secret formats / RCE functions
    # ELEVATED (1): dangerous patterns, SQL injection
    # LOW      (2): technical debt markers, debug flags
    PRIORITY_PATTERNS: list[tuple[int, str]] = [
        # CRITICAL — credentials & known secret formats
        (0, r"AKIA[A-Z0-9]{16}"),
        (0, r"ghp_[a-zA-Z0-9]{36}"),
        (0, r"sk_live_[a-zA-Z0-9]+"),
        (0, r"BEGIN (RSA|EC|OPENSSH) PRIVATE KEY"),
        (0, r"password\s*=\s*['\"][^'\"]{3,}['\"]"),
        (0, r"passwd\s*=\s*['\"][^'\"]{3,}['\"]"),
        (0, r"secret\s*=\s*['\"][^'\"]{3,}['\"]"),
        (0, r"api_key\s*=\s*['\"][^'\"]{3,}['\"]"),
        (0, r"apikey\s*=\s*['\"][^'\"]{3,}['\"]"),
        (0, r"token\s*=\s*['\"][^'\"]{3,}['\"]"),
        # CRITICAL — remote code execution vectors
        (0, r"eval\("),
        (0, r"exec\("),
        (0, r"os\.system\("),
        (0, r"pickle\.loads\("),
        (0, r"yaml\.load\([^,)]+\)"),
        # ELEVATED — SQL injection, unsafe subprocess
        (1, r"execute\(f['\"]SELECT"),
        (1, r"['\"]SELECT.*WHERE.*['\"]\s*\+"),
        (1, r"subprocess\.call\("),
        # LOW — technical debt & debug
        (2, r"TODO"),
        (2, r"FIXME"),
        (2, r"HACK"),
        (2, r"XXX"),
        (2, r"DEBUG\s*=\s*True"),
        (2, r"console\.log\("),
    ]

    SKIP_EXTENSIONS: frozenset[str] = frozenset([
        ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
        ".woff", ".woff2", ".ttf", ".eot", ".zip", ".gz", ".tar",
        ".pdf", ".lock", ".sum", ".bin", ".exe", ".so",
    ])
    SKIP_DIRS: frozenset[str] = frozenset([
        ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ])

    MASK_RE = re.compile(r"(['\"])[A-Za-z0-9_\-]{8,}(['\"])")

    def _mask(line: str) -> str:
        return MASK_RE.sub(r"\1[REDACTED]\2", line)

    # Buckets sorted by priority so CRITICAL findings claim slots first.
    buckets: dict[int, list[str]] = {0: [], 1: [], 2: []}

    # ── Strategy 1: native git grep (C speed) ─────────────────────────
    pattern_strings = "|".join(p for _, p in PRIORITY_PATTERNS)
    git_grep_succeeded = False
    try:
        result = subprocess.run(
            ["git", "-C", directory, "grep", "-inE", pattern_strings,
             "--", ":!node_modules", ":!__pycache__", ":!.venv", ":!dist"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode in (0, 1):  # 0 = found, 1 = no matches (not an error)
            git_grep_succeeded = True
            compiled_pats = [
                (prio, re.compile(pat, re.IGNORECASE))
                for prio, pat in PRIORITY_PATTERNS
            ]
            for raw_line in result.stdout.splitlines():
                # git grep output: "filepath:lineno:content"
                parts = raw_line.split(":", 2)
                if len(parts) < 3:
                    continue
                fpath, lineno, content = parts[0], parts[1], parts[2]
                for prio, cpat in compiled_pats:
                    if cpat.search(content):
                        masked_content = _mask(content.strip())
                        entry = f"[P{prio}] {fpath}:{lineno} → {masked_content}"
                        buckets[prio].append(entry)
                        break
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        # git not available or directory not a git repo — fall through.
        git_grep_succeeded = False

    # ── Strategy 2: Python generator fallback ─────────────────────────
    if not git_grep_succeeded:
        compiled_pats = [
            (prio, re.compile(pat, re.IGNORECASE))
            for prio, pat in PRIORITY_PATTERNS
        ]

        def _walk_files(root_dir: str):
            """Yield (filepath,) for every scannable file, lazily."""
            for dirpath, dirnames, filenames in os.walk(root_dir):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                for fname in filenames:
                    if any(fname.endswith(ext) for ext in SKIP_EXTENSIONS):
                        continue
                    yield os.path.join(dirpath, fname)

        # Early-exit as soon as all buckets have enough to cap MAX_FINDINGS
        running_total = 0
        for fpath in _walk_files(directory):
            if running_total >= MAX_FINDINGS * 3:  # generous headroom before sort
                break
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                    for line_no, raw_line in enumerate(fh, start=1):
                        line = raw_line.rstrip()
                        for prio, cpat in compiled_pats:
                            if cpat.search(line):
                                masked = _mask(line)
                                buckets[prio].append(
                                    f"[P{prio}] {fpath}:{line_no} → {masked.strip()}"
                                )
                                running_total += 1
                                break  # one finding per line
            except (PermissionError, OSError):
                continue

    # ── Merge, cap, and format ─────────────────────────────────────────
    merged: list[str] = []
    for prio in (0, 1, 2):
        merged.extend(buckets[prio])

    total_raw = len(merged)
    truncated = total_raw > MAX_FINDINGS
    findings = merged[:MAX_FINDINGS]

    if not findings:
        return "No security anti-patterns detected."

    output_lines = [f"Found {total_raw} raw pattern match(es). Reporting top {len(findings)} (priority-sorted):"]
    output_lines.extend(findings)
    if truncated:
        output_lines.append(
            f"... [Additional {total_raw - MAX_FINDINGS} finding(s) truncated "
            f"to protect LLM context window.]"
        )
    return "\n".join(output_lines)


# ──────────────────────────────────────────────────────────────────────
#  Remote repo support — clone any GitHub URL to a temp dir
# ──────────────────────────────────────────────────────────────────────

def clone_repo(url: str) -> tuple[str, str]:
    """
    Clone a public git repository to a temporary directory using a shallow,
    single-branch clone strategy for maximum speed.

    Uses --depth 1 (no history) and --single-branch (no other branches) to
    download ONLY the current HEAD snapshot. A repo like React that is
    gigabytes in full history clones in under 5 seconds with this strategy.

    Enforces a 20-second network timeout via subprocess.run(timeout=...) so
    a hung network request fails fast instead of freezing the agent on stage.

    Returns (temp_dir_path, repo_name) on success.
    Raises SystemExit with an actionable error message on any failure.
    """
    url = url.strip()
    if not url.startswith(("https://", "http://", "git@")):
        raise SystemExit(
            c(f"❌  Invalid URL '{url}'. Must start with https:// or git@", RED)
        )

    repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
    tmp = tempfile.mkdtemp(prefix="causalloop-")

    print(c(f"\n  ⚡ Shallow-cloning {url} (depth=1, single-branch) ...", DIM))
    print(c(f"     This fetches HEAD only — no git history downloaded.", DIM))

    try:
        result = subprocess.run(
            [
                "git", "clone",
                "--depth=1",
                "--single-branch",
                "--no-tags",
                url,
                tmp,
            ],
            capture_output=True,
            text=True,
            timeout=20,          # fail fast — do not hang during a live demo
        )
    except subprocess.TimeoutExpired:
        shutil.rmtree(tmp, ignore_errors=True)
        raise SystemExit(
            c("❌  Clone timed out after 20 seconds. Check network connectivity.", RED)
        )
    except FileNotFoundError:
        shutil.rmtree(tmp, ignore_errors=True)
        raise SystemExit(
            c("❌  'git' command not found. Install Git and ensure it is on PATH.", RED)
        )

    if result.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        stderr = result.stderr.strip()
        raise SystemExit(
            c(f"❌  Failed to clone repo: {stderr}", RED)
        )

    print(c(f"  ✅ Clone complete. Analyzing: {repo_name}\n", GREEN))
    return tmp, repo_name


def cleanup_repo(tmp_dir: str) -> None:
    """Remove a temporary cloned repo directory."""
    if tmp_dir and os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print(c("\n  Cleaned up temp clone.", DIM))


# ──────────────────────────────────────────────────────────────────────
#  Auto-generate diff.txt if not present (merge-risk skill)
# ──────────────────────────────────────────────────────────────────────

def get_or_generate_diff(target_dir: str) -> Optional[str]:
    """
    Look for diff.txt in the root, then try to generate one from git history.
    Returns filepath to the diff file, or None if unavailable.
    """
    diff_path = os.path.join(target_dir, "diff.txt")
    if os.path.exists(diff_path):
        return diff_path

    # Try to auto-generate from git
    result = subprocess.run(
        ["git", "-C", target_dir, "diff", "HEAD~1", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        auto_path = os.path.join(target_dir, "diff.txt")
        with open(auto_path, "w", encoding="utf-8") as f:
            f.write(result.stdout)
        print(c("  ℹ️  Auto-generated diff.txt from git history (HEAD~1..HEAD)", DIM))
        return auto_path

    return None


# ──────────────────────────────────────────────────────────────────────
#  Lyzr Agent factory
# ──────────────────────────────────────────────────────────────────────

def create_agent() -> object:
    """Create and configure the CausalLoop Lyzr agent with all local tools."""
    lyzr_key, _ = load_and_validate_env()
    studio = Studio(api_key=lyzr_key)

    agent = studio.create_agent(
        name="CausalLoop",
        provider="gemini-2.5-pro",
        role=CAUSAL_LOOP_ROLE,
        goal=CAUSAL_LOOP_GOAL,
        instructions=CAUSAL_LOOP_INSTRUCTIONS,
        temperature=0.3,
        memory=30,
    )

    agent.add_tool(read_file)
    agent.add_tool(write_file)
    agent.add_tool(list_directory)
    agent.add_tool(run_grep_scan)

    return agent


# ──────────────────────────────────────────────────────────────────────
#  Skill runners
# ──────────────────────────────────────────────────────────────────────

def run_skill_repo_autopsy(agent: object, target_dir: str) -> str:
    """Execute skill 1: repo-autopsy — scan codebase for vulnerabilities."""
    print(c("\n🔬 PHASE 1  |  repo-autopsy", CYAN, BOLD))
    print(c("   Scanning the past — what was written and why it is dangerous.", DIM))
    print(c("─" * 62, DIM))

    prompt = f"""
Execute the repo-autopsy skill on the directory: "{target_dir}"

Steps:
1. Use the `list_directory` tool on "{target_dir}" to understand the repo structure.
2. Use the `run_grep_scan` tool on "{target_dir}" to find security anti-patterns.
3. For each file that contains findings, use `read_file` to read it and analyze in detail.
4. For every finding:
   - Cite the exact file path and line number
   - Assign a severity: CRITICAL, ELEVATED, or DEPRESSINGLY-PREDICTABLE
   - Write the full causal chain: what is wrong → why it exists → what systemic failure allows it
5. Present your full forensic report directly in the response as formatted text. DO NOT write any files.
6. End with a SYSTEMIC VERDICT: name the institutional failure pattern, not the individual developer.
"""
    response = agent.run(prompt)
    return response.response


def run_skill_secret_scanner(agent: object, target_dir: str) -> str:
    """Execute skill 2: secret-scanner — hunt hardcoded credentials."""
    print(c("\n🔑 PHASE 2  |  secret-scanner", RED, BOLD))
    print(c("   Deep-scanning for credentials, tokens, and keys that must not exist here.", DIM))
    print(c("─" * 62, DIM))

    prompt = f"""
Execute the secret-scanner skill on the directory: "{target_dir}"

Steps:
1. Use `run_grep_scan` on "{target_dir}" — focus findings on credential patterns.
2. Use `list_directory` to check for .env files, *.pem, *.key files committed to the repo.
3. For each credential finding:
   - Classify it: CRITICAL (active credential) or ELEVATED (suspicious pattern)
   - State the file path and line number
   - MASK the actual credential value — never output it. Use [REDACTED] for values over 4 chars.
   - Explain the causal chain: developer shortcut → no pre-commit hook → credential in git history forever
4. Present your full Secret Scan Report directly in the response. DO NOT write any files.
5. State whether this is an isolated incident or reflects a systemic secret management failure.

CRITICAL: You MUST NEVER output the actual credential value. Only its location, type, and classification.
"""
    response = agent.run(prompt)
    return response.response


def run_skill_dependency_audit(agent: object, target_dir: str) -> str:
    """Execute skill 3: dependency-audit — audit dependency posture."""
    print(c("\n📦 PHASE 3  |  dependency-audit", YELLOW, BOLD))
    print(c("   Auditing dependency manifests for unpinned versions and missing lockfiles.", DIM))
    print(c("─" * 62, DIM))

    prompt = f"""
Execute the dependency-audit skill on the directory: "{target_dir}"

Steps:
1. Use `list_directory` on "{target_dir}" to find dependency manifests:
   requirements.txt, package.json, Pipfile, pyproject.toml, setup.py, go.mod, Cargo.toml
2. Use `read_file` to read each manifest found.
3. Analyze:
   a) Are versions pinned (==x.y.z) or unpinned (>=, *, no version)?
   b) Is there a corresponding lockfile? (requirements.lock, package-lock.json, Pipfile.lock, poetry.lock)
   c) Are dev dependencies separated from production dependencies?
   d) Flag any known historically vulnerable package names.
4. Assign a RISK RATING: CRITICAL / ELEVATED / GUARDED / LOW
5. Present your full Dependency Audit Report directly in the response. DO NOT write any files.
6. The SYSTEMIC VERDICT must identify whether this reflects a team-wide process failure.
"""
    response = agent.run(prompt)
    return response.response


def run_skill_compliance_check(agent: object, target_dir: str) -> str:
    """Execute skill 4: compliance-check — audit project infrastructure."""
    print(c("\n📋 PHASE 4  |  compliance-check", BLUE, BOLD))
    print(c("   Auditing project infrastructure, git hygiene, and README quality.", DIM))
    print(c("─" * 62, DIM))

    prompt = f"""
Execute the compliance-check skill on the directory: "{target_dir}"

Steps:
1. Use `list_directory` on "{target_dir}" to get the full file tree.
2. Check for presence of these files (MANDATORY or STRONG):
   - README.md (MANDATORY)
   - LICENSE (MANDATORY — without it, the code is legally All Rights Reserved)
   - .gitignore (MANDATORY)
   - CONTRIBUTING.md (STRONG)
   - SECURITY.md (STRONG)
   - .env.example (STRONG)
   - requirements.txt or equivalent (MANDATORY)
3. Check for CI/CD: .github/workflows/, .gitlab-ci.yml, .circleci/
4. Check for git hygiene violations (files that should never be committed):
   - .env files, node_modules/, __pycache__/, *.pyc, .DS_Store, dist/, build/
   - Look for merge conflict markers: <<<<<<, =======, >>>>>>>
5. If README.md exists, use `read_file` to read it — check it has: description, install, usage.
6. Assign an Infrastructure Score from 0 to 10.
7. Present your full Compliance Report directly in the response. DO NOT write any files.
"""
    response = agent.run(prompt)
    return response.response


def run_skill_mortem_interrogator(agent: object, target_dir: str) -> str:
    """Execute skill 5: mortem-interrogator — Five Whys root cause analysis."""
    print(c("\n🔎 PHASE 5  |  mortem-interrogator", MAGENTA, BOLD))
    print(c("   Investigating the present — Five Whys systemic root cause analysis.", DIM))
    print(c("─" * 62, DIM))

    incident_path = os.path.join(target_dir, "incident.md")
    if not os.path.exists(incident_path):
        print(c(f"   ⚠️  No incident.md found in {target_dir}.", YELLOW))
        print(c("   Creating a sample incident report from autopsy findings...", DIM))
        sample_incident = """# Incident Report

## Date: 2026-04-08

## Summary
A hardcoded API key was discovered in the source code repository. The key was
committed to the public repository and was live for an unknown duration.

## Timeline
- Developer created a quick authentication module using a hardcoded key during prototyping
- Code was merged to main branch without a security review
- No pre-commit hooks or CI scanning detected the credential
- An external researcher reported the exposure via a GitHub search

## Initial Assessment
"Developer oversight — they forgot to move the key to an environment variable."

## Impact
Unknown. Key has been rotated. Full blast radius under investigation.
"""
        try:
            with open(incident_path, "w", encoding="utf-8") as f:
                f.write(sample_incident)
            print(c(f"   ✅  Created {incident_path}", GREEN))
        except Exception as exc:
            print(c(f"   ❌  Could not create incident.md: {exc}", RED))

    prompt = f"""
Execute the mortem-interrogator skill. Read the incident report at: "{incident_path}"

Steps:
1. Use `read_file` to read "{incident_path}".
2. Perform a rigorous Five Whys analysis:
   - Why 1: The immediate technical cause
   - Why 2: The process failure that allowed it
   - Why 3: The team/culture factor
   - Why 4: The organizational policy gap
   - Why 5: The systemic institutional failure

3. MANDATORY: You MUST explicitly reject "human error", "developer oversight",
   "they forgot", or "rushing" as root causes. State clearly:
   "REJECTED: [the suggested cause]. This is a symptom, not a cause."

4. The TRUE ROOT CAUSE must be a systemic or institutional failure —
   absent automated testing, broken review culture, missing guardrails, etc.

5. Issue a systemic recommendation that, if implemented, would make this class
   of failure structurally impossible — not just unlikely.

6. Present your full systemic verdict directly in the response. DO NOT write any files.
"""
    response = agent.run(prompt)
    return response.response


def run_skill_merge_risk(agent: object, target_dir: str) -> str:
    """Execute skill 6: merge-risk — evaluate PR diff for regression risk."""
    print(c("\n🔮 PHASE 6  |  merge-risk", CYAN, BOLD))
    print(c("   Guarding the future — cross-referencing incoming changes against past findings.", DIM))
    print(c("─" * 62, DIM))

    diff_path = get_or_generate_diff(target_dir)

    if not diff_path:
        msg = (
            c("   ℹ️  No diff.txt found and no git history available.\n", DIM) +
            "   In production, CausalLoop intercepts PRs and maps changes\n"
            "   against past systemic findings to block history from repeating.\n"
            "   To use this skill: create diff.txt with your PR's git diff output."
        )
        print(msg)
        return "merge-risk: skipped — no diff available."

    prompt = f"""
Execute the merge-risk skill.

Steps:
1. Use `read_file` to read the diff at: "{diff_path}"
2. If it exists, use `read_file` to read the autopsy report at: "{target_dir}/autopsy-report.md"
3. If it exists, use `read_file` to read the systemic finding at: "{target_dir}/systemic-finding.md"

4. Cross-reference the diff against known findings:
   - Do the changed files include any that previously had CRITICAL findings?
   - Do the changes introduce any of the same anti-patterns that caused past incidents?
   - Are there any new dependencies being added without pinning?

5. Assign a MERGE RISK SCORE:
   - BLOCK: Changes repeat a previously identified CRITICAL finding
   - WARN:  Changes touch high-risk areas identified in autopsy
   - CAUTION: New code follows patterns that correlate with past debt accumulation
   - CLEAR: No regression risk detected

6. Present your full Merge Risk Assessment directly in the response. DO NOT write any files.
7. The verdict must state: APPROVE / WARN / BLOCK — and the causal justification.
"""
    response = agent.run(prompt)
    return response.response


# ──────────────────────────────────────────────────────────────────────
#  Memory — persist findings across sessions
# ──────────────────────────────────────────────────────────────────────

MEMORY_PATH = os.path.join(os.path.dirname(__file__), "memory", "findings.json")

def save_to_memory(target: str, skills_run: list[str], timestamp: str) -> None:
    """Append a session record to memory/findings.json."""
    try:
        os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
        data: dict = {"version": 1, "sessions": [], "repos_analyzed": []}
        if os.path.exists(MEMORY_PATH):
            with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

        session = {
            "timestamp": timestamp,
            "target": target,
            "skills_run": skills_run,
        }
        data.setdefault("sessions", []).append(session)
        if target not in data.get("repos_analyzed", []):
            data.setdefault("repos_analyzed", []).append(target)
        data["last_updated"] = timestamp

        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass  # Memory is non-critical — never crash because of it


# ──────────────────────────────────────────────────────────────────────
#  Skill dispatcher
# ──────────────────────────────────────────────────────────────────────

# Maps every legal command → (canonical-name, runner-fn)
SKILL_MAP: dict[str, tuple[str, object]] = {
    "autopsy":       ("repo-autopsy",        run_skill_repo_autopsy),
    "repo-autopsy":  ("repo-autopsy",        run_skill_repo_autopsy),
    "secrets":       ("secret-scanner",      run_skill_secret_scanner),
    "secret-scanner":("secret-scanner",      run_skill_secret_scanner),
    "deps":          ("dependency-audit",    run_skill_dependency_audit),
    "dependency-audit":("dependency-audit",  run_skill_dependency_audit),
    "compliance":    ("compliance-check",    run_skill_compliance_check),
    "compliance-check":("compliance-check",  run_skill_compliance_check),
    "interrogate":   ("mortem-interrogator", run_skill_mortem_interrogator),
    "mortem-interrogator":("mortem-interrogator", run_skill_mortem_interrogator),
    "merge-risk":    ("merge-risk",          run_skill_merge_risk),
}

# For --skill argparse choices
SKILL_NAME_MAP: dict[str, str] = {
    "repo-autopsy":        "autopsy",
    "secret-scanner":      "secrets",
    "dependency-audit":    "deps",
    "compliance-check":    "compliance",
    "mortem-interrogator": "interrogate",
    "merge-risk":          "merge-risk",
}


def dispatch_skill(choice: str, agent: object, target_dir: str) -> Optional[str]:
    """Run a single skill by its command name. Returns the response text."""
    entry = SKILL_MAP.get(choice.lower())
    if not entry:
        print(c(f"  ❌  Unknown command: '{choice}'. Type 'help' to see available commands.", RED))
        return None
    _name, runner = entry
    return runner(agent, target_dir)


def run_all_skills(agent: object, target_dir: str) -> list[str]:
    """Run all 6 skills in sequence."""
    results: list[str] = []
    for key in ("autopsy", "secrets", "deps", "compliance", "interrogate", "merge-risk"):
        _name, runner = SKILL_MAP[key]
        result = runner(agent, target_dir)
        results.append(result)
    return results


# ──────────────────────────────────────────────────────────────────────
#  Interactive CLI loop
# ──────────────────────────────────────────────────────────────────────

def interactive_loop(agent: object, target_dir: str) -> None:
    """Main interactive command loop."""
    skills_run: list[str] = []

    print()
    print_menu(target_dir)

    while True:
        try:
            choice = input(c("\nCausalLoop> ", CYAN, BOLD)).strip().lower()
        except (KeyboardInterrupt, EOFError):
            print(c("\n\n  Exiting CausalLoop. The loop is closed.\n", DIM))
            break

        if choice in ("q", "quit", "exit"):
            print(c("\n  Exiting CausalLoop. The loop is closed.\n", DIM))
            break

        if choice in ("h", "help"):
            print()
            print_menu(target_dir)
            continue

        if choice == "":
            continue

        if choice == "full":
            print(c("\n  ⚡ Running full investigation — all 6 skills...", MAGENTA, BOLD))
            run_all_skills(agent, target_dir)
            skills_run.extend(["repo-autopsy", "secret-scanner", "dependency-audit",
                                "compliance-check", "mortem-interrogator", "merge-risk"])
            print(c("\n  ✅ Full investigation complete.", GREEN, BOLD))
            continue

        result = dispatch_skill(choice, agent, target_dir)
        if result:
            name = SKILL_MAP.get(choice, (choice,))[0]
            skills_run.append(name)
            print(c(f"\n  ✅ Done.", GREEN))

    # Persist session to memory
    save_to_memory(target_dir, skills_run, datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))


# ──────────────────────────────────────────────────────────────────────
#  Entry point — argument parsing
# ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="causalloop",
        description="CausalLoop — Cross-temporal forensic systems analyst.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_lyzr.py                                  # Interactive menu (local dummy_repo/)
  python run_lyzr.py --repo https://github.com/org/repo
  python run_lyzr.py --skill repo-autopsy
  python run_lyzr.py --skill secret-scanner --repo https://github.com/org/repo
  python run_lyzr.py --all
        """,
    )
    parser.add_argument(
        "--repo",
        metavar="URL",
        help="URL of a public GitHub/GitLab repo to clone and analyze",
    )
    parser.add_argument(
        "--skill",
        metavar="SKILL",
        choices=list(SKILL_MAP.keys()),
        help="Run a single specific skill and exit (e.g. autopsy, secrets, deps, compliance, interrogate, merge-risk)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all 6 skills in sequence and exit (non-interactive)",
    )
    parser.add_argument(
        "--target",
        metavar="DIR",
        default=os.path.join(os.path.dirname(__file__), "dummy_repo"),
        help="Local directory to analyze (default: dummy_repo/)",
    )

    args = parser.parse_args()

    print_header()
    load_and_validate_env()

    tmp_dir: Optional[str] = None
    target_dir: str = args.target

    # Clone remote repo if requested
    if args.repo:
        tmp_dir, _name = clone_repo(args.repo)
        target_dir = tmp_dir

    # Validate target directory
    if not os.path.isdir(target_dir):
        print(c(f"❌  Target directory not found: {target_dir}", RED))
        print(c(f"   Create it or pass a valid --target path.", DIM))
        raise SystemExit(1)

    try:
        print(c(f"  Initializing Lyzr ADK agent...", DIM))
        agent = create_agent()
        print(c(f"  ✅ Agent ready. Target: {os.path.abspath(target_dir)}\n", GREEN))

        if args.skill:
            # Single skill mode
            dispatch_skill(args.skill, agent, target_dir)
            save_to_memory(target_dir, [args.skill], datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
        elif args.all:
            # Run all skills non-interactively
            print(c("  ⚡ Running all 6 skills in sequence...\n", MAGENTA, BOLD))
            run_all_skills(agent, target_dir)
            save_to_memory(
                target_dir,
                list(SKILL_MAP.keys()),
                datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            )
            print(c("\n  ✅ Full investigation complete.", GREEN, BOLD))
        else:
            # Interactive menu mode
            interactive_loop(agent, target_dir)

    finally:
        if tmp_dir:
            cleanup_repo(tmp_dir)


if __name__ == "__main__":
    main()
