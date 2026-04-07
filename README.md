# CausalLoop 🕵️‍♂️

> "The AI assistant that figures out why things broke yesterday, what might break tomorrow, and how to stop your team from making the same mistake twice."

**CausalLoop** is an AI designed to act like a strict but helpful detective for your project. Instead of just pointing out that something is broken, it digs deep to find the real, hidden reason behind why the mistake happened in the first place.

It has the patience of an airplane crash investigator. It won't accept "human error" or "we were rushing" as a valid excuse. Instead, it looks for missing safeguards—like a lack of automated testing or poor review processes—that allowed the mistake to happen.

## What Can CausalLoop Do?

CausalLoop looks at your project across three different timelines: **The Past**, **The Present**, and **The Future**.

### 1. Checking the Past (`repo-autopsy`)
CausalLoop acts like a code inspector, carefully reading through your existing code. It looks for hidden problems, like accidental security flaws or hardcoded passwords that shouldn't be there. It then quickly writes a report pointing out exactly which files and lines of code need to be fixed.

### 2. Investigating the Present (`mortem-interrogator`)
If a problem happens and your team writes down notes about it (called an incident report), CausalLoop will read those notes and constantly ask "Why?". It traces the problem all the way back to the core issue. It ignores excuses and focuses entirely on what broken process or missing rule allowed the failure to occur. 

### 3. Protecting the Future (`merge-risk`)
Before your team adds new changes to the project, CausalLoop double-checks the new code. It compares your new changes to past mistakes and warns you if it looks like you are about to accidentally break things again. 

## How CausalLoop Thinks (Core Rules)

- **Find the Real Problem:** Fixing just the symptom isn't enough; finding the root cause is required.
- **Failures aren't Flukes:** If something breaks, it's usually a repeating pattern, not just an accident.
- **Show Proof:** Every claim the AI makes must be backed up with exact proof from the code.
- **No Sugar-Coating:** If the team makes the exact same mistake twice, it means the rules need to change. 

## Quick Start

### What you need
Make sure you have downloaded the GitClaw tool by running this in your terminal:
```bash
npm install gitclaw
```

### Try it out
You can check if CausalLoop is set up correctly by running these commands:
```bash
npx gitagent validate
npx gitagent info
```

Provide the AI with a dummy project or an incident report file, and let CausalLoop start investigating your project!
