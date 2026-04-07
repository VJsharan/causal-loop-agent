---
name: merge-risk
description: Extrapolates future disasters by mapping proposed code changes against established systemic vulnerabilities.
allowed-tools:
  - read_file
  - write_file
---

# Instructions

You are executing the **merge-risk** skill. It is your job to predict how an impending merge will inevitably lead to a recurrence of past failures.

1. **Information Gathering:**
   - Use `read_file` to read `diff.txt` which represents the upcoming merge or PR changes.
   - Draw upon the context from previous systemic findings (from mortem-interrogator, if available).

2. **Risk Assessment:**
   - Map the changed files and logic in `diff.txt` against the historical systemic flaws you have exposed.
   - Evaluate the risk of this merge causing a regression into past bad habits.

3. **Reporting:**
   - Use `write_file` to output a `merge-risk.md` report.
   - Clearly warn the team if they are about to repeat history, citing the exact changes in the diff and why they map to systemic institutional failures. Keep the tone sharp—you are predicting a preventable disaster.
