"""
CausalLoop Agent — Powered by Lyzr ADK + Gemini

A cross-temporal forensic systems analyst that:
  1. Scans the past  (repo-autopsy)     → finds vulnerabilities in code
  2. Investigates the present (mortem-interrogator) → traces incidents to systemic root causes
  3. Protects the future (merge-risk)   → warns if new changes repeat old mistakes
"""

import os
import re
import subprocess
from dotenv import load_dotenv
from lyzr import Studio

# ──────────────────────────────────────────────────────────────────────
#  Load environment
# ──────────────────────────────────────────────────────────────────────
load_dotenv()

LYZR_API_KEY = os.getenv("LYZR_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not LYZR_API_KEY or LYZR_API_KEY.startswith("your_"):
    raise SystemExit("❌  Set LYZR_API_KEY in .env  (get one free at https://studio.lyzr.ai)")
if not GOOGLE_API_KEY or GOOGLE_API_KEY.startswith("your_"):
    raise SystemExit("❌  Set GOOGLE_API_KEY in .env  (get one free at https://aistudio.google.com)")


# ──────────────────────────────────────────────────────────────────────
#  CausalLoop identity (from SOUL.md + RULES.md)
# ──────────────────────────────────────────────────────────────────────
CAUSAL_LOOP_ROLE = (
    "Cross-temporal forensic systems analyst. "
    "You think in causal chains, not snapshots. "
    "You possess the cynicism of an experienced forensic analyst, "
    "the unyielding patience of an NTSB investigator, "
    "and the foresight of someone who has watched the exact same class of failure recur across ten different organizations."
)

CAUSAL_LOOP_GOAL = (
    "Expose the true systemic and institutional root causes behind every code failure, "
    "security vulnerability, and incident. Fix the system, not the symptom."
)

CAUSAL_LOOP_INSTRUCTIONS = """
You are CausalLoop — a cross-temporal forensic systems analyst.

COMMUNICATION STYLE:
- Evidence first, conclusion second. Every claim has a source — cite it relentlessly.
- Speak in causal language: never say "this is broken." Say "this broke because of X, which will cause Y unless Z is addressed."
- Deliver one finding at a time. Never bury the lead. Sharp, precise, no sugar-coating.

ABSOLUTE RULES — MUST ALWAYS:
- Trace every finding to a causal origin. Explain not just WHAT failed, but WHY and HOW the condition persists.
- Distinguish clearly between past failures, present risks, and future predictions.
- Cite the exact file, line number, or incident timeline entry for every claim. Opinions without citations are null and void.

ABSOLUTE RULES — MUST NEVER:
- Accept the proximate cause as the true root cause. Push deeper.
- Generate a risk finding without a step-by-step causal explanation.
- Close an investigation without issuing a systemic recommendation to prevent recurrence.
- Attribute failure to "human error" — human error is a consequence of insufficient guardrails.
"""

# ──────────────────────────────────────────────────────────────────────
#  Local tools — these run on YOUR machine and give the agent real power
# ──────────────────────────────────────────────────────────────────────

def read_file(filepath: str) -> str:
    """Read the contents of a local file and return it as text."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"ERROR: File '{filepath}' not found."
    except Exception as e:
        return f"ERROR reading '{filepath}': {e}"


def write_file(filepath: str, content: str) -> str:
    """Write content to a local file. Creates the file if it doesn't exist."""
    try:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{filepath}'."
    except Exception as e:
        return f"ERROR writing '{filepath}': {e}"


def list_directory(directory: str) -> str:
    """List all files and subdirectories in a given directory."""
    try:
        entries = os.listdir(directory)
        return "\n".join(entries) if entries else "(empty directory)"
    except FileNotFoundError:
        return f"ERROR: Directory '{directory}' not found."
    except Exception as e:
        return f"ERROR listing '{directory}': {e}"


def run_grep_scan(directory: str) -> str:
    """
    Scan a directory for common security anti-patterns using grep.
    Looks for: hardcoded passwords, eval(), exec(), TODO/FIXME, API keys, secrets.
    """
    patterns = [
        "password",
        "secret",
        "api_key",
        "eval(",
        "exec(",
        "TODO",
        "FIXME",
        "hardcoded",
        "admin",
    ]
    results = []
    for root, _dirs, files in os.walk(directory):
        for fname in files:
            if not fname.endswith((".py", ".js", ".ts", ".java", ".go", ".rb", ".yaml", ".yml", ".json", ".env")):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, start=1):
                        for pattern in patterns:
                            if pattern.lower() in line.lower():
                                results.append(f"[{pattern}] {fpath}:{i} → {line.rstrip()}")
            except Exception:
                continue

    if not results:
        return "No security anti-patterns found."
    return "\n".join(results)


# ──────────────────────────────────────────────────────────────────────
#  Initialize Lyzr Studio + Create the Agent
# ──────────────────────────────────────────────────────────────────────

def create_causal_loop_agent():
    """Create and configure the CausalLoop agent via Lyzr ADK."""
    studio = Studio(api_key=LYZR_API_KEY)

    agent = studio.create_agent(
        name="CausalLoop",
        provider="gemini-2.5-pro",
        role=CAUSAL_LOOP_ROLE,
        goal=CAUSAL_LOOP_GOAL,
        instructions=CAUSAL_LOOP_INSTRUCTIONS,
        temperature=0.3,       # Low temp → precise, deterministic forensic analysis
        memory=30,             # Remember context across skill executions
    )

    # Register local tools so the agent can read/write/scan files on your machine
    agent.add_tool(read_file)
    agent.add_tool(write_file)
    agent.add_tool(list_directory)
    agent.add_tool(run_grep_scan)

    return agent


# ──────────────────────────────────────────────────────────────────────
#  Demo runner — executes all 3 skills sequentially
# ──────────────────────────────────────────────────────────────────────

def run_demo():
    print("=" * 60)
    print("  CausalLoop — Forensic Systems Analyst")
    print("  Powered by Lyzr ADK + Gemini 2.5 Pro")
    print("=" * 60)

    agent = create_causal_loop_agent()

    # ── SKILL 1: The Past (repo-autopsy) ─────────────────────────────
    print("\n🔬 PHASE 1: Scanning the Past (repo-autopsy)")
    print("-" * 50)

    autopsy_prompt = """
    Execute the repo-autopsy skill.

    1. Use the `run_grep_scan` tool on the "dummy_repo/" directory to scan for security anti-patterns.
    2. Use the `read_file` tool to read "dummy_repo/auth.py" and analyze its contents line by line.
    3. For every finding, cite the exact file path and line number, assign a severity
       (CRITICAL, ELEVATED, or DEPRESSINGLY-PREDICTABLE), and explain the causal chain
       of why this vulnerability exists and what systemic failure allowed it.
    4. Use the `write_file` tool to save your full forensic report to "autopsy-report.md".
    """

    response = agent.run(autopsy_prompt)
    print(response.response)

    # ── SKILL 2: The Present (mortem-interrogator) ───────────────────
    print("\n🔎 PHASE 2: Investigating the Present (mortem-interrogator)")
    print("-" * 50)

    interrogator_prompt = """
    Execute the mortem-interrogator skill.

    1. Use the `read_file` tool to read "incident.md".
    2. Perform a rigorous Five Whys analysis on the incident described.
    3. CRITICAL RULE: You MUST explicitly reject any attribution to "human error",
       "developer typo", "rushing", or "we didn't know". These are symptoms, not causes.
    4. Trace the failure back to systemic or institutional flaws (e.g., lack of automated
       testing, poor code review culture, broken CI/CD pipelines, absent guardrails).
    5. Use the `write_file` tool to save your verdict to "systemic-finding.md".
    """

    response = agent.run(interrogator_prompt)
    print(response.response)

    # ── SKILL 3: The Future (merge-risk) ─────────────────────────────
    print("\n🔮 PHASE 3: Protecting the Future (merge-risk)")
    print("-" * 50)

    # Check if diff.txt exists; if not, explain the stub
    if os.path.exists("diff.txt"):
        merge_prompt = """
        Execute the merge-risk skill.

        1. Use `read_file` to read "diff.txt" which represents upcoming merge changes.
        2. Cross-reference the changed files against findings from the repo-autopsy
           and the systemic root causes from the mortem-interrogator.
        3. Evaluate the risk: are these changes about to repeat the same institutional
           mistakes that caused the last incident?
        4. Use `write_file` to output your warning to "merge-risk.md".
        """
        response = agent.run(merge_prompt)
        print(response.response)
    else:
        print("   ℹ️  No diff.txt found — merge-risk is stubbed for the demo.")
        print("   In production, CausalLoop would intercept PRs and map changes")
        print("   against systemic findings to block history from repeating.\n")

    print("\n" + "=" * 60)
    print("  ✅ Demo Complete — All CausalLoop skills executed.")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
