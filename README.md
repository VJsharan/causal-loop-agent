<div align="center">

# 🕵️‍♂️ CausalLoop

### The AI That Refuses to Blame Humans

[![Lyzr ADK](https://img.shields.io/badge/Lyzr_ADK-v0.1.8-4F46E5?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiLz48L3N2Zz4=)](https://docs.lyzr.ai/lyzr-adk/overview)
[![Gemini 2.5 Pro](https://img.shields.io/badge/Gemini_2.5_Pro-Google-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![GitAgent](https://img.shields.io/badge/GitAgent-Standard-F97316?style=for-the-badge&logo=git&logoColor=white)](https://gitagent.sh)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

---

**CausalLoop** is an AI forensic agent that investigates code failures the way the NTSB investigates plane crashes.

It doesn't care who wrote the bug. It cares about **why the system allowed the bug to exist.**

> *"Human error is not a root cause. It is a consequence of insufficient guardrails."*
> — CausalLoop, every single time.

</div>

---

## 🧠 What Does CausalLoop Actually Do?

Most tools say *"you have a bug on line 7."*

CausalLoop says *"the bug on line 7 exists because your CI pipeline has zero static analysis, your team has no enforced code review policy, and your deadline pressure systematically incentivizes shipping unsafe code."*

It works across **three timelines**:

| Phase | Skill | What It Does | Output |
|-------|-------|-------------|--------|
| 🔬 **The Past** | `repo-autopsy` | Scans your codebase for security flaws, hardcoded secrets, and tech debt | `autopsy-report.md` |
| 🔎 **The Present** | `mortem-interrogator` | Reads incident reports and performs a Five Whys analysis to find the *real* root cause | `systemic-finding.md` |
| 🔮 **The Future** | `merge-risk` | Compares incoming code changes against past findings to warn before you repeat mistakes | `merge-risk.md` |

---

## ⚡ How It Works

```
                    ┌─────────────────────┐
                    │     Your Codebase    │
                    │  (dummy_repo/*.py)   │
                    └────────┬────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │      🔬 repo-autopsy         │
              │  grep scan → read files →    │
              │  cite lines → assign blame   │
              └──────────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ autopsy-report │
                    │     .md        │
                    └────────┬───────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                                    │
           ▼                                    ▼
┌─────────────────────┐            ┌──────────────────────┐
│ 🔎 mortem-           │            │ 🔮 merge-risk        │
│    interrogator      │            │    (future PRs)      │
│                      │            │                      │
│ incident.md →        │            │ diff.txt →           │
│ Five Whys →          │            │ cross-reference →    │
│ reject excuses →     │            │ predict failures →   │
│ systemic verdict     │            │ block repeats        │
└──────────┬──────────┘            └──────────┬───────────┘
           │                                    │
           ▼                                    ▼
  ┌──────────────────┐              ┌──────────────────┐
  │ systemic-finding │              │   merge-risk     │
  │      .md         │              │      .md         │
  └──────────────────┘              └──────────────────┘
```

All three skills are powered by **Lyzr ADK** + **Google Gemini 2.5 Pro**, with local Python tools that give the agent real filesystem access to read code sets, run scans, and write reports live.

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology | Why |
|-------|-----------|-----|
| 🤖 **Agent Framework** | [Lyzr ADK](https://docs.lyzr.ai/lyzr-adk/overview) | Native agent creation, memory, tools, and RAI guardrails |
| 🧠 **LLM** | [Gemini 2.5 Pro](https://aistudio.google.com) | Google's most capable model — free tier available |
| 📐 **Agent Standard** | [GitAgent](https://gitagent.sh) | Git-native agent definition — version-controlled identity |
| 🐍 **Runtime** | Python 3.10+ | Local tool execution for file I/O and security scanning |

</div>

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- A free [Lyzr API key](https://studio.lyzr.ai) (Community plan — no credit card)
- A free [Gemini API key](https://aistudio.google.com)

### 1. Clone the repo

```bash
git clone https://github.com/VJsharan/causal-loop-agent.git
cd causal-loop-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API keys

Open the `.env` file and replace the placeholders:

```env
LYZR_API_KEY=your_lyzr_api_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. Run the agent

```bash
python run_lyzr.py
```

That's it. CausalLoop will spin up, scan the dummy repo, interrogate the incident report, and write its findings to disk — all in under 60 seconds. ⚡

---

## 🎯 Sample Output

When you run the agent against the included `dummy_repo/auth.py`:

```
============================================================
  CausalLoop — Forensic Systems Analyst
  Powered by Lyzr ADK + Gemini 2.5 Pro
============================================================

🔬 PHASE 1: Scanning the Past (repo-autopsy)
--------------------------------------------------
[CRITICAL] dummy_repo/auth.py:3 → Hardcoded admin credentials
[CRITICAL] dummy_repo/auth.py:7 → eval() with unsanitized user input
...

🔎 PHASE 2: Investigating the Present (mortem-interrogator)
--------------------------------------------------
REJECTED: "developer was rushing" is not a root cause.
VERDICT: Absence of automated SAST in CI/CD pipeline...

🔮 PHASE 3: Protecting the Future (merge-risk)
--------------------------------------------------
ℹ️  No diff.txt found — stubbed for demo.

============================================================
  ✅ Demo Complete — All CausalLoop skills executed.
============================================================
```

---

## 🧬 Agent Identity

CausalLoop's personality is defined by two files that live in git:

### `SOUL.md` — Who it is

> A cross-temporal forensic analyst with the cynicism of someone who has watched the exact same class of failure recur across ten different organizations. It thinks in causal chains, not snapshots.

### `RULES.md` — What it must always do

| ✅ Must Always | ❌ Must Never |
|---------------|--------------|
| Trace every finding to a causal origin | Accept the proximate cause as the root cause |
| Cite exact file paths, line numbers, or timeline entries | Generate findings without step-by-step explanations |
| Distinguish past failures, present risks, and future predictions | Attribute failure to "human error" |
| Issue systemic recommendations to prevent recurrence | Close an investigation without a fix recommendation |

---

## 📂 Project Structure

```
causal-loop-agent/
│
├── 🤖 agent.yaml              # GitAgent manifest — model, skills, metadata
├── 🧠 SOUL.md                 # Agent persona & personality definition
├── 📏 RULES.md                # Behavioral constraints & investigation rules
│
├── 🐍 run_lyzr.py             # Main entry — Lyzr ADK + Gemini execution
├── 📦 requirements.txt        # Python dependencies (lyzr-adk, python-dotenv)
├── 🔑 .env                    # API keys (never committed)
│
├── 📁 dummy_repo/
│   └── auth.py                # Intentionally flawed code for demo scanning
│
├── 📄 incident.md             # Sample incident report for Five Whys analysis
│
├── 📁 skills/
│   ├── repo-autopsy/
│   │   └── SKILL.md           # Instructions for codebase forensic scan
│   ├── mortem-interrogator/
│   │   └── SKILL.md           # Instructions for incident root cause analysis
│   └── merge-risk/
│       └── SKILL.md           # Instructions for pre-merge risk assessment
│
└── 📊 Generated Reports (after running)
    ├── autopsy-report.md      # Forensic findings from code scan
    ├── systemic-finding.md    # Root cause verdict from incident analysis
    └── merge-risk.md          # Pre-merge risk warnings (when diff.txt exists)
```

---

## 🔑 Key Features

- 🔍 **Real File System Access** — The agent reads, scans, and writes files on your actual machine via Lyzr's local tool execution
- 🧠 **Conversational Memory** — Maintains context across all three skill phases so findings build on each other
- 🛡️ **Rejection of "Human Error"** — Hardcoded as a rule: the agent must always dig deeper than blaming people
- 📐 **Git-Native Identity** — Agent persona, rules, and skills are all version-controlled markdown files
- ⚡ **Zero Cost** — Runs entirely on free tiers of Lyzr (Community) and Google Gemini

---

## 🏗️ Built With

<div align="center">

| | |
|---|---|
| ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) | Core runtime and local tools |
| ![Lyzr](https://img.shields.io/badge/Lyzr_ADK-4F46E5?style=for-the-badge) | Agent framework with memory, tools, and guardrails |
| ![Google](https://img.shields.io/badge/Gemini_2.5_Pro-4285F4?style=for-the-badge&logo=google&logoColor=white) | LLM backbone for forensic reasoning |
| ![Git](https://img.shields.io/badge/GitAgent-F05032?style=for-the-badge&logo=git&logoColor=white) | Open standard for agent definition |

</div>

---

## 📜 License

This project is open source under the [MIT License](LICENSE).

---

<div align="center">

**Built for the Lyzr × GitAgent Hackathon**

*Stop blaming developers. Start fixing systems.*

🔬 → 🔎 → 🔮

</div>
