<div align="center">

<h1>🕵️‍♂️ CausalLoop</h1>

<p><strong>The AI That Refuses to Blame Humans.</strong></p>

<p><em>CausalLoop investigates code failures the way the NTSB investigates plane crashes. It doesn't care who wrote the bug. It cares about why the system allowed the bug to exist.</em></p>

<br/>

<!-- BADGES -->
<div align="center">
<table>
  <tr>
    <td align="center"><a href="https://github.com/VJsharan/causal-loop-agent"><img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white"/></a></td>
    <td align="center"><a href="https://docs.lyzr.ai/lyzr-adk/overview"><img src="https://img.shields.io/badge/Lyzr_ADK-v0.1.8-4F46E5?style=for-the-badge"/></a></td>
    <td align="center"><a href="https://aistudio.google.com"><img src="https://img.shields.io/badge/Gemini_2.5_Pro-Google-4285F4?style=for-the-badge&logo=google&logoColor=white"/></a></td>
    <td align="center"><a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge"/></a></td>
    <td align="center"><a href="https://gitagent.sh"><img src="https://img.shields.io/badge/GitAgent-Standard-F97316?style=for-the-badge&logo=git&logoColor=white"/></a></td>
  </tr>
</table>
</div>

<br/>

</div>

---

## 🧠 What is this?

`CausalLoop` is a dual-runtime (Python & Node.js) forensic AI agent that **lives inside your terminal** - defined using the [gitagent open standard](https://github.com/open-gitagent/gitagent). It reads your codebase and open GitHub issues, turning raw structural failures into systemic institutional verdicts.

**What makes it different?** While others just lint code or point fingers at developers, CausalLoop executes **high-speed ephemeral shallow clones** (`--depth=1`) of massive public repositories in seconds, intercepts live production fires from the GitHub API, and conducts rigorous *Five Whys* root cause analysis. It strictly refuses to accept "human error" as a verdict.

> *"Human error is not a root cause. It is a consequence of insufficient guardrails."*
> — CausalLoop

---

## 📚 Table of Contents

- [What is this?](#-what-is-this)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Forensic Skills](#-forensic-skills)
- [How It Works](#-how-it-works)
- [Configuration](#-configuration)
- [Built With](#-built-with)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

<div align="center">

| Skill | What it does | Goal |
|---|---|---|
| `repo-autopsy` 🔬 | Scans codebase for security anti-patterns (regex speed) | Identify existing vulnerabilities |
| `secret-scanner` 🔑 | Hunts hardcoded credentials & API keys | Prevent credentials in git history |
| `dependency-audit` 📦 | Audits dependency posture & lockfiles | Evaluate supply-chain risk |
| `compliance-check` 📋 | Audits project infrastructure & git hygiene | Enforce branch rules & CI presence |
| `mortem-interrogator` 🔎 | Interrogates live bugs via GitHub API & Five Whys | Find the true systemic failure |
| `merge-risk` 🔮 | Evaluates incoming PR diffs for regression risk | Guard against repeating past errors |

</div>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ / Node.js 18+
- Git installed and in PATH
- A free [Lyzr API key](https://studio.lyzr.ai)
- A free [Gemini API key](https://aistudio.google.com)

### Installation

```bash
# 1. Clone the agent
git clone https://github.com/VJsharan/causal-loop-agent.git
cd causal-loop-agent

# 2. Install Python dependencies (for Lyzr backend)
pip install -r requirements.txt

# 3. Add your API keys
echo "LYZR_API_KEY=your_key_here" >> .env
echo "GOOGLE_API_KEY=your_key_here" >> .env

# 4. Run the interactive CLI (Node.js)
node index.js
```

At startup, you'll enter the fully interactive CLI. Press `[r]` to analyze any public GitHub URL on the fly, or just select a skill to scan the local `dummy_repo`.

### Running the Pure Python Lyzr Backend

```bash
# Run one specific skill on a public repo
python run_lyzr.py --repo https://github.com/django/django --skill secrets

# Run all 6 skills in sequence
python run_lyzr.py --repo https://github.com/django/django --all
```

---

## 🤖 Forensic Skills

<div align="center">
<table>
<tr>
<td align="center" width="33%"><a href="#-repo-autopsy"><img src="https://img.shields.io/badge/🔬_REPO_AUTOPSY-534AB7?style=for-the-badge&logoColor=EEEDFE"/></a><br/><sub>Scans the past codebase for fatal patterns</sub></td>
<td align="center" width="33%"><a href="#-secret-scanner"><img src="https://img.shields.io/badge/🔑_SECRET_SCANNER-A32D2D?style=for-the-badge"/></a><br/><sub>Hunts credentials & active private keys</sub></td>
<td align="center" width="33%"><a href="#-dependency-audit"><img src="https://img.shields.io/badge/📦_DEPENDENCY_AUDIT-0F6E56?style=for-the-badge"/></a><br/><sub>Validates supply-chain architecture</sub></td>
</tr>
<tr>
<td align="center"><a href="#-compliance-check"><img src="https://img.shields.io/badge/📋_COMPLIANCE_CHECK-185FA5?style=for-the-badge"/></a><br/><sub>Audits institutional git hygiene</sub></td>
<td align="center"><a href="#-mortem-interrogator"><img src="https://img.shields.io/badge/🔎_MORTEM_INTERROGATOR-993556?style=for-the-badge"/></a><br/><sub>Fetches GitHub issues & runs Five Whys</sub></td>
<td align="center"><a href="#-merge-risk"><img src="https://img.shields.io/badge/🔮_MERGE_RISK-854F0B?style=for-the-badge"/></a><br/><sub>Pre-merge risk warnings on incoming diffs</sub></td>
</tr>
</table>
</div>

---

## 🏗️ How It Works

```mermaid
flowchart TD
    START["🔗 CLI / Python Entry\nEnter GitHub URL or local path"]:::start

    R1["📁 Local Repo"]:::git
    R2["🌐 Public Repo\n(shallow clone depth=1)"]:::git

    A["🧠 Agent Identity"]:::identity
    A1["SOUL.md\nPersonality"]:::file
    A2["RULES.md\nConstraints"]:::file

    B["⚙️ Lyzr Core / Node Router\n(Dual Engine)"]:::runtime
    C["⚡ Native Fast Grep\n(P0 priority capped)"]:::gitlog
    D["🤖 Gemini 2.5 Pro\n(Lyzr ADK)"]:::llm
    E["📡 GitHub REST API\n(Live Bug Polling)"]:::api

    OUT["📺 Terminal Output\nDirectly streamed"]:::output

    START --> R1 & R2
    R1 & R2 --> C
    A1 & A2 --> A
    C --> B
    E --> B
    A --> B
    B --> D
    D --> OUT

    classDef start fill:#064e3b,stroke:#10b981,color:#d1fae5
    classDef identity fill:#1e1b4b,stroke:#6366f1,color:#e0e7ff
    classDef file fill:#312e81,stroke:#818cf8,color:#c7d2fe
    classDef runtime fill:#1e3a5f,stroke:#38bdf8,color:#e0f2fe
    classDef git fill:#14532d,stroke:#4ade80,color:#dcfce7
    classDef gitlog fill:#1a2e05,stroke:#84cc16,color:#ecfccb
    classDef llm fill:#7c2d12,stroke:#fb923c,color:#ffedd5
    classDef api fill:#581c87,stroke:#c084fc,color:#fae8ff
    classDef output fill:#111827,stroke:#374151,color:#9ca3af
```

1. **At startup**, choose to analyze the local codebase or input a public GitHub repository. The software executes a sub-3-second *ephemeral shallow clone*.
2. **Context Assembly**: It intercepts live bugs from the GitHub API and uses `git grep -inE` inside a priority-bucket system (P0: keys, P1: vectors, P2: debt) to scan massive codebases safely.
3. **Agent execution**: Powered by Gemini 2.5 Pro and Lyzr ADK, it runs a rigorous *Five Whys* interrogation and streams terminal output directly to you.
4. **Clean up**: All temporary clone trails are strictly swept up after execution.

---

## 🔧 Configuration

### Environment Variables

<div align="center">

| Variable | Required | Description |
|---|---|---|
| `LYZR_API_KEY` | ✅ Yes | Your Lyzr ADK key - [get one free](https://studio.lyzr.ai) |
| `GOOGLE_API_KEY` | ✅ Yes | Your Gemini API key for logic synthesis |

</div>

---

## 🧩 Built With

<div align="center">

| Technology | Purpose |
|:---:|:---|
| [![Lyzr](https://img.shields.io/badge/Lyzr_ADK-4F46E5?style=for-the-badge)](https://docs.lyzr.ai/lyzr-adk/overview) | Agent persistence, routing, and guardrails |
| [![Google](https://img.shields.io/badge/Gemini_2.5_Pro-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com) | LLM inference backend |
| [![gitagent](https://img.shields.io/badge/gitagent-Standard-F97316?style=for-the-badge)](https://github.com/open-gitagent/gitagent) | Version-controlled AI personality definition |
| [![Python/Node](https://img.shields.io/badge/Dual_Runtime-Python_&_Node-3B6D11?style=for-the-badge)](#) | Cross-language environment compatibility |

</div>

---

## 🤝 Contributing

Contributions, issues, and feature requests are highly welcome! Review the `RULES.md` file before submitting PRs—human error is still strictly prohibited.

---

## 📄 License

<div align="center">

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>
