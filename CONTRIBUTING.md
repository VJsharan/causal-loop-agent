# Contributing to CausalLoop

Thanks for your interest in contributing to CausalLoop — the AI forensic agent that refuses to blame humans.

## How to Contribute

1. **Fork** the repo
2. **Create a branch**
   ```bash
   git checkout -b feat/your-feature
   ```
3. **Commit with a clear message**
   ```bash
   git commit -m "feat: add dependency-audit skill"
   ```
4. **Push and open a Pull Request**

## Adding a New Skill

1. Create `skills/your-skill/SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: your-skill
   description: What this skill does.
   allowed-tools:
     - read_file
     - write_file
     - run_grep_scan
   ---
   ```
2. Add the skill name to `agent.yaml` under `skills:`
3. Wire the prompt into `run_lyzr.py` under the interactive CLI menu
4. Add a demo output file to `demo-output/`

## Project Structure

```
causal-loop-agent/
├── agent.yaml              # GitAgent manifest
├── SOUL.md                 # Agent identity
├── RULES.md                # Behavioral constraints
├── run_lyzr.py             # Main entry point (Lyzr ADK + Gemini)
├── skills/                 # Skill definitions (SKILL.md per skill)
├── tools/                  # Tool YAML schemas
├── knowledge/              # Reference knowledge base
├── memory/                 # Cross-session findings cache
├── dummy_repo/             # Intentionally flawed demo codebase
└── demo-output/            # Pre-generated sample reports
```

## Code Standards

- All Python functions must have full type hints
- All file operations must be wrapped in try/except
- No silent failures — always return an error string the LLM can understand
- No hardcoded paths, secrets, or model names — use environment variables

## Reporting Issues

Open an issue with:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
