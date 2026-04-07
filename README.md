# CausalLoop 🕵️‍♂️

> "The AI assistant that figures out why things broke yesterday, what might break tomorrow, and how to stop your team from making the same mistake twice."

**CausalLoop** is an AI agent built with the [Lyzr ADK](https://docs.lyzr.ai/lyzr-adk/overview) and powered by **Google Gemini 2.5 Pro**. It follows the [GitAgent](https://gitagent.sh) open standard — meaning its identity, skills, and rules all live as version-controlled files in this git repo.

Instead of just pointing out that something is broken, CausalLoop digs deep to find the real, hidden reason behind why the mistake happened in the first place. It won't accept "human error" or "we were rushing" as an excuse. It looks for missing safeguards that allowed the mistake to happen.

## What Can CausalLoop Do?

CausalLoop looks at your project across three timelines: **The Past**, **The Present**, and **The Future**.

### 1. Checking the Past (`repo-autopsy`)
CausalLoop scans your codebase for security flaws, hardcoded passwords, dangerous functions like `eval()`, and technical debt. It writes a forensic report (`autopsy-report.md`) citing exact file paths, line numbers, and severity ratings.

### 2. Investigating the Present (`mortem-interrogator`)
When an incident happens and your team writes notes about it (`incident.md`), CausalLoop reads those notes and keeps asking "Why?" until it finds the real systemic root cause. It ignores excuses and focuses entirely on what broken process or missing rule allowed the failure to occur. Output: `systemic-finding.md`.

### 3. Protecting the Future (`merge-risk`)
Before your team adds new changes, CausalLoop compares the diff against past mistakes and warns you if you're about to accidentally break things again. Output: `merge-risk.md`.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Agent Framework** | [Lyzr ADK](https://docs.lyzr.ai/lyzr-adk/overview) |
| **LLM Provider** | Google Gemini 2.5 Pro |
| **Agent Standard** | [GitAgent](https://gitagent.sh) (git-native agent definition) |
| **Runtime** | [GitClaw](https://github.com/open-gitagent/gitclaw) (optional CLI) |

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up your API keys
Edit the `.env` file and add your keys:
```
LYZR_API_KEY=your_lyzr_api_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
```
- **Lyzr key**: Sign up free at [Lyzr Studio](https://studio.lyzr.ai) → Account & API Key
- **Gemini key**: Get one free at [Google AI Studio](https://aistudio.google.com)

### 3. Run the demo
```bash
python run_lyzr.py
```

This runs all three CausalLoop skills in sequence:
1. Scans `dummy_repo/auth.py` for vulnerabilities → generates `autopsy-report.md`
2. Reads `incident.md` and performs a Five Whys analysis → generates `systemic-finding.md`
3. (If `diff.txt` exists) Evaluates merge risk → generates `merge-risk.md`

## Core Rules

- **Find the Real Problem:** Fixing just the symptom isn't enough; finding the root cause is required.
- **Failures aren't Flukes:** If something breaks, it's usually a repeating pattern, not just an accident.
- **Show Proof:** Every claim the AI makes must be backed up with exact proof from the code.
- **No Sugar-Coating:** If the team makes the exact same mistake twice, the rules need to change.

## Project Structure
```
causal-loop/
├── agent.yaml          # GitAgent manifest (model, skills, tags)
├── SOUL.md             # Agent identity & personality
├── RULES.md            # Behavioral constraints
├── run_lyzr.py         # Main entry point (Lyzr ADK + Gemini)
├── .env                # API keys (not committed)
├── requirements.txt    # Python dependencies
├── dummy_repo/
│   └── auth.py         # Intentionally flawed code for demo
├── incident.md         # Sample incident report for demo
└── skills/
    ├── repo-autopsy/SKILL.md
    ├── mortem-interrogator/SKILL.md
    └── merge-risk/SKILL.md
```
