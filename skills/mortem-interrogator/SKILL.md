---
name: mortem-interrogator
description: Interrogates an incident report using the Five Whys framework to extract the uncomfortable systemic root cause. Rejects human error as an excuse.
allowed-tools:
  - read_file
  - write_file
---

# Instructions

You are executing the **mortem-interrogator** skill. A generic incident report will be provided to you. You must uncover the true, systemic root cause that management typically avoids acknowledging.

1. **Information Gathering:**
   - Use `read_file` to read the target incident markdown file (usually `incident.md`).

2. **The Interrogation (Five Whys):**
   - Internally execute a "Five Whys" analysis based on the incident text.
   - Trace the failure from the proximate cause down to its absolute systemic foundation.
   - **CRITICAL RULE:** You MUST explicitly reject explanations like "human error", "developer typo", "we didn't know", or "ran out of time" as root causes.
   - You MUST trace the failure back to a systemic or institutional flaw (e.g., lack of automated testing, poor code review culture, broken CI/CD pipelines, lack of mandatory guardrails).

3. **Reporting:**
   - Use `write_file` to generate your verdict into `systemic-finding.md`.
   - Your output must explicitly condemn the institutional flaw and clarify that the incident was merely a symptom.
