#!/usr/bin/env node
/**
 * CausalLoop — Node.js Runtime
 *
 * Dual-runtime entry point for the CausalLoop forensic agent.
 * This runner is compatible with the gitagent open standard and can be
 * invoked directly, via `node index.js`, or via `gitclaw`.
 *
 * For the full Lyzr ADK + Gemini 2.5 Pro experience, use:
 *   python run_lyzr.py
 *
 * Usage:
 *   node index.js                          # Interactive menu
 *   node index.js --skill repo-autopsy     # Single skill, non-interactive
 *   node index.js --repo <github_url>      # Analyze a remote repo
 *   node index.js --all                    # All 6 skills in sequence
 *   gitclaw --dir . "scan this repo for vulnerabilities"
 */

import { GoogleGenerativeAI } from "@google/generative-ai";
import { config } from "dotenv";
import { execSync, spawnSync } from "child_process";
import {
  readFileSync,
  writeFileSync,
  existsSync,
  readdirSync,
  statSync,
  mkdtempSync,
  rmSync,
} from "fs";
import { createInterface } from "readline";
import { tmpdir } from "os";
import { join, dirname, basename, extname } from "path";
import { fileURLToPath } from "url";

config();

const __filename = fileURLToPath(import.meta.url);
const __dirname  = dirname(__filename);

// ─────────────────────────────────────────────────────────────
//  ANSI colours
// ─────────────────────────────────────────────────────────────

const C = {
  reset:   "\x1b[0m",
  bold:    "\x1b[1m",
  dim:     "\x1b[2m",
  red:     "\x1b[91m",
  yellow:  "\x1b[93m",
  green:   "\x1b[92m",
  cyan:    "\x1b[96m",
  blue:    "\x1b[94m",
  magenta: "\x1b[95m",
  white:   "\x1b[97m",
};

const paint = (text, ...codes) => codes.join("") + text + C.reset;

// ─────────────────────────────────────────────────────────────
//  ASCII header
// ─────────────────────────────────────────────────────────────

const HEADER = `
${C.cyan}${C.bold}
   ██████╗ █████╗ ██╗   ██╗███████╗ █████╗ ██╗     
  ██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗██║     
  ██║     ███████║██║   ██║███████╗███████║██║     
  ██║     ██╔══██║██║   ██║╚════██║██╔══██║██║     
  ╚██████╗██║  ██║╚██████╔╝███████║██║  ██║███████╗
   ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝
${C.reset}${C.cyan}${C.bold}  ██╗      ██████╗  ██████╗ ██████╗ 
  ██║     ██╔═══██╗██╔═══██╗██╔══██╗
  ██║     ██║   ██║██║   ██║██████╔╝
  ██║     ██║   ██║██║   ██║██╔═══╝ 
  ███████╗╚██████╔╝╚██████╔╝██║     
  ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝     
${C.reset}${C.dim}        Cross-Temporal Forensic Systems Analyst  [Node.js Runtime]
        Powered by Gemini API  ·  gitagent compatible
        Refuses to blame humans. Always.${C.reset}
`;

// ─────────────────────────────────────────────────────────────
//  Environment validation
// ─────────────────────────────────────────────────────────────

const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY;
if (!GOOGLE_API_KEY || GOOGLE_API_KEY.startsWith("your_")) {
  console.error(
    paint("\n❌  GOOGLE_API_KEY not set.", C.red) +
    "\n   Copy .env.example → .env and add your key." +
    "\n   Free key at: https://aistudio.google.com\n"
  );
  process.exit(1);
}

// ─────────────────────────────────────────────────────────────
//  Gemini client
// ─────────────────────────────────────────────────────────────

const genAI  = new GoogleGenerativeAI(GOOGLE_API_KEY);
const MODELS = [
  "gemini-3.1-flash-lite-preview",
  "gemini-2.5-pro",
  "gemini-2.5-flash",
  "gemini-2.0-flash",
  "gemini-1.5-flash",
];

/**
 * Call Gemini with automatic model fallback.
 * @param {string} systemPrompt
 * @param {string} userMessage
 * @returns {Promise<string>}
 */
async function callGemini(systemPrompt, userMessage) {
  for (const modelName of MODELS) {
    try {
      const model = genAI.getGenerativeModel({
        model: modelName,
        systemInstruction: systemPrompt,
      });
      const result = await model.generateContent(userMessage);
      return result.response.text();
    } catch (err) {
      if (err.status === 429 || err.status === 503) {
        console.log(paint(`  ⚠  ${modelName} rate-limited, trying next model…`, C.yellow));
        continue;
      }
      throw err;
    }
  }
  throw new Error("All Gemini models exhausted.");
}

// ─────────────────────────────────────────────────────────────
//  Agent identity loader (reads SOUL.md + RULES.md + all SKILLs)
// ─────────────────────────────────────────────────────────────

function loadIdentity() {
  const soulPath  = join(__dirname, "SOUL.md");
  const rulesPath = join(__dirname, "RULES.md");

  if (!existsSync(soulPath) || !existsSync(rulesPath)) {
    console.error(paint("❌  SOUL.md or RULES.md not found.", C.red));
    process.exit(1);
  }

  const soul  = readFileSync(soulPath,  "utf8");
  const rules = readFileSync(rulesPath, "utf8");

  const skillDirs = [
    "skills/repo-autopsy",
    "skills/secret-scanner",
    "skills/dependency-audit",
    "skills/compliance-check",
    "skills/mortem-interrogator",
    "skills/merge-risk",
  ];

  const skills = skillDirs
    .map(d => join(__dirname, d, "SKILL.md"))
    .filter(existsSync)
    .map(p => readFileSync(p, "utf8"))
    .join("\n\n---\n\n");

  const knowledgePath = join(__dirname, "knowledge", "security-patterns.md");
  const knowledge = existsSync(knowledgePath)
    ? readFileSync(knowledgePath, "utf8")
    : "";

  return [
    "You are CausalLoop — a cross-temporal forensic systems analyst.",
    soul,
    rules,
    knowledge ? `## Knowledge Base\n\n${knowledge}` : "",
    skills ? `## Your Skills\n\n${skills}` : "",
  ].filter(Boolean).join("\n\n---\n\n");
}

// ─────────────────────────────────────────────────────────────
//  Local repo tools (pure JS, no shell dependencies)
// ─────────────────────────────────────────────────────────────

const SKIP_DIRS = new Set([".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"]);
const SKIP_EXTS = new Set([".pyc", ".png", ".jpg", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".zip", ".gz", ".pdf", ".lock"]);

/**
 * Recursively list all files in a directory.
 * @param {string} dir
 * @param {string} [prefix=""]
 * @returns {string}
 */
function listDirectory(dir, prefix = "") {
  if (!existsSync(dir)) return `ERROR: directory '${dir}' not found.`;
  const lines = [];
  try {
    const entries = readdirSync(dir);
    for (const entry of entries) {
      if (SKIP_DIRS.has(entry)) continue;
      const full = join(dir, entry);
      const stat = statSync(full);
      if (stat.isDirectory()) {
        lines.push(`${prefix}${entry}/`);
        lines.push(listDirectory(full, prefix + "  "));
      } else {
        lines.push(`${prefix}${entry}`);
      }
    }
  } catch { /* permission error */ }
  return lines.join("\n");
}

const CREDENTIAL_PATTERNS = [
  /password\s*=\s*['"][^'"]{3,}['"]/i,
  /passwd\s*=\s*['"][^'"]{3,}['"]/i,
  /secret\s*=\s*['"][^'"]{3,}['"]/i,
  /api_key\s*=\s*['"][^'"]{3,}['"]/i,
  /apikey\s*=\s*['"][^'"]{3,}['"]/i,
  /token\s*=\s*['"][^'"]{3,}['"]/i,
  /AKIA[A-Z0-9]{16}/,
  /ghp_[a-zA-Z0-9]{36}/,
  /sk_live_[a-zA-Z0-9]+/,
  /BEGIN (RSA|EC|OPENSSH) PRIVATE KEY/,
  /eval\(/,
  /exec\(/,
  /os\.system\(/,
  /pickle\.loads\(/,
  /TODO/,
  /FIXME/,
  /HACK/,
  /DEBUG\s*=\s*True/i,
];

/**
 * Scan a directory for security anti-patterns.
 * @param {string} dir
 * @returns {string}
 */
function runGrepScan(dir) {
  const findings = [];

  function walk(current) {
    if (!existsSync(current)) return;
    const entries = readdirSync(current);
    for (const entry of entries) {
      if (SKIP_DIRS.has(entry)) continue;
      const full = join(current, entry);
      const stat = statSync(full);
      if (stat.isDirectory()) {
        walk(full);
      } else {
        if (SKIP_EXTS.has(extname(entry))) continue;
        try {
          const lines = readFileSync(full, "utf8").split("\n");
          lines.forEach((line, i) => {
            for (const pat of CREDENTIAL_PATTERNS) {
              if (pat.test(line)) {
                const masked = line.replace(/(['"])[A-Za-z0-9_\-]{8,}(['"])/g, "'[REDACTED]'");
                findings.push(`[${pat.source.slice(0, 25)}] ${full}:${i + 1} → ${masked.trim()}`);
                break;
              }
            }
          });
        } catch { /* skip unreadable */ }
      }
    }
  }

  walk(dir);
  if (findings.length === 0) return "No security anti-patterns detected.";
  return `Found ${findings.length} pattern(s):\n${findings.join("\n")}`;
}

/**
 * Read a file and return its contents.
 * @param {string} filepath
 * @returns {string}
 */
function readFile(filepath) {
  if (!existsSync(filepath)) return `ERROR: '${filepath}' not found.`;
  try {
    return readFileSync(filepath, "utf8");
  } catch (e) {
    return `ERROR reading '${filepath}': ${e.message}`;
  }
}

/**
 * Write content to a file (creates directories as needed).
 * @param {string} filepath
 * @param {string} content
 * @returns {string}
 */
function writeFile(filepath, content) {
  try {
    writeFileSync(filepath, content, "utf8");
    return `OK: Wrote ${content.length.toLocaleString()} chars to '${filepath}'.`;
  } catch (e) {
    return `ERROR writing '${filepath}': ${e.message}`;
  }
}

// ─────────────────────────────────────────────────────────────
//  Remote repo support
// ─────────────────────────────────────────────────────────────

let tempDir = null;

function cloneRepo(url) {
  url = url.trim();
  if (!url.startsWith("https://") && !url.startsWith("http://") && !url.startsWith("git@")) {
    throw new Error(`Invalid URL '${url}'. Must start with https:// or git@`);
  }
  console.log(paint(`\n  ⚡ Shallow-cloning ${url} (depth=1, single-branch) …`, C.dim));
  tempDir = mkdtempSync(join(tmpdir(), "causalloop-"));
  const result = spawnSync("git", ["clone", "--depth=1", "--single-branch", "--no-tags", url, tempDir], {
    encoding: "utf8",
    stdio: "pipe",
    timeout: 20000,
  });
  if (result.status !== 0) {
    rmSync(tempDir, { recursive: true, force: true });
    tempDir = null;
    const msg = result.error && result.error.code === "ETIMEDOUT" 
      ? "Clone timed out after 20 seconds. Check network connectivity." 
      : ((result.stderr || "") + (result.error ? " " + result.error.message : "")).trim() || "Unknown git error";
    throw new Error(`Clone failed: ${msg}`);
  }
  const name = url.replace(/\/$/, "").split("/").pop().replace(".git", "");
  console.log(paint(`  ✅ Clone complete. Target set to: ${name}\n`, C.green));
  return tempDir;
}

function cleanup() {
  if (tempDir) {
    try { rmSync(tempDir, { recursive: true, force: true }); } catch { /* ignore */ }
    console.log(paint("\n  Cleaned up temp clone.", C.dim));
  }
}

// ─────────────────────────────────────────────────────────────
//  Diff generator for merge-risk
// ─────────────────────────────────────────────────────────────

function getOrGenerateDiff(targetDir) {
  const diffPath = join(targetDir, "diff.txt");
  if (existsSync(diffPath)) return diffPath;

  try {
    const diff = execSync(`git -C "${targetDir}" diff HEAD~1 HEAD`, { encoding: "utf8" });
    if (diff.trim()) {
      writeFileSync(diffPath, diff, "utf8");
      console.log(paint("  ℹ️  Auto-generated diff.txt from git history (HEAD~1..HEAD)", C.dim));
      return diffPath;
    }
  } catch { /* no git history */ }

  return null;
}

// ─────────────────────────────────────────────────────────────
//  Skill runners
// ─────────────────────────────────────────────────────────────

async function runRepoAutopsy(systemPrompt, targetDir) {
  console.log(paint("\n🔬 SKILL  |  repo-autopsy", C.cyan, C.bold));
  console.log(paint("   Scanning the past — what was written and why it is dangerous.", C.dim));
  console.log(paint("   " + "─".repeat(58), C.dim));

  const structure = listDirectory(targetDir);
  const scanResults = runGrepScan(targetDir);

  const userMsg = `
Execute the repo-autopsy skill on: "${targetDir}"

Repository structure:
${structure}

Security scan results:
${scanResults}

For every finding:
- Cite the exact file path and line number
- Assign severity: CRITICAL, ELEVATED, or DEPRESSINGLY-PREDICTABLE
- Write the full causal chain: what is wrong → why it exists → what systemic failure allows it

Save the full forensic report to "${targetDir}/autopsy-report.md" (write the markdown yourself).
End with a SYSTEMIC VERDICT naming the institutional failure, not the individual.
`;

  const reply = await callGemini(systemPrompt, userMsg);
  console.log(reply);

  const reportPath = join(targetDir, "autopsy-report.md");
  if (!existsSync(reportPath)) {
    writeFile(reportPath, reply);
  }
  console.log(paint(`\n  ✅ Report saved to autopsy-report.md`, C.green));
  return reply;
}

async function runSecretScanner(systemPrompt, targetDir) {
  console.log(paint("\n🔑 SKILL  |  secret-scanner", C.red, C.bold));
  console.log(paint("   Deep-scanning for credentials, tokens, and keys that must not exist here.", C.dim));
  console.log(paint("   " + "─".repeat(58), C.dim));

  const scanResults = runGrepScan(targetDir);
  const structure   = listDirectory(targetDir);

  const userMsg = `
Execute the secret-scanner skill on: "${targetDir}"

Repository structure (check for .env, *.pem, *.key files):
${structure}

Security scan results:
${scanResults}

For each credential finding:
- Classify: CRITICAL (active credential) or ELEVATED (suspicious pattern)
- State file path and line number
- MASK credential values with [REDACTED] — never output the actual value
- State the causal chain: shortcut → no pre-commit hook → credential in git history forever

Save the Secret Scan Report to "${targetDir}/secret-scan-report.md".
CRITICAL: Never output actual credential values.
`;

  const reply = await callGemini(systemPrompt, userMsg);
  console.log(reply);
  writeFile(join(targetDir, "secret-scan-report.md"), reply);
  console.log(paint(`\n  ✅ Report saved to secret-scan-report.md`, C.green));
  return reply;
}

async function runDependencyAudit(systemPrompt, targetDir) {
  console.log(paint("\n📦 SKILL  |  dependency-audit", C.yellow, C.bold));
  console.log(paint("   Auditing dependency manifests for unpinned versions and missing lockfiles.", C.dim));
  console.log(paint("   " + "─".repeat(58), C.dim));

  const manifestFiles = [
    "requirements.txt", "requirements.lock", "Pipfile", "Pipfile.lock",
    "pyproject.toml", "poetry.lock", "package.json", "package-lock.json",
    "yarn.lock", "go.mod", "go.sum", "Cargo.toml", "Cargo.lock",
  ];

  const manifests = {};
  for (const mf of manifestFiles) {
    const p = join(targetDir, mf);
    if (existsSync(p)) manifests[mf] = readFile(p);
  }

  const userMsg = `
Execute the dependency-audit skill on: "${targetDir}"

Dependency manifests found:
${Object.entries(manifests).map(([k, v]) => `\n=== ${k} ===\n${v}`).join("\n") || "No manifests found."}

Analyze:
1. Are versions pinned (==x.y.z) or unpinned (>=, *, no version)?
2. Is there a lockfile for each manifest?
3. Are dev dependencies separated from production?
4. Flag any known historically vulnerable package names.

Assign RISK RATING: CRITICAL / ELEVATED / GUARDED / LOW.
Save the Dependency Audit Report to "${targetDir}/dependency-audit-report.md".
`;

  const reply = await callGemini(systemPrompt, userMsg);
  console.log(reply);
  writeFile(join(targetDir, "dependency-audit-report.md"), reply);
  console.log(paint(`\n  ✅ Report saved to dependency-audit-report.md`, C.green));
  return reply;
}

async function runComplianceCheck(systemPrompt, targetDir) {
  console.log(paint("\n📋 SKILL  |  compliance-check", C.blue, C.bold));
  console.log(paint("   Auditing project infrastructure, git hygiene, and README quality.", C.dim));
  console.log(paint("   " + "─".repeat(58), C.dim));

  const structure = listDirectory(targetDir);
  const readmePath = join(targetDir, "README.md");
  const readme     = existsSync(readmePath) ? readFile(readmePath).slice(0, 2000) : "NOT FOUND";

  const userMsg = `
Execute the compliance-check skill on: "${targetDir}"

Full repository structure:
${structure}

README.md (first 2000 chars):
${readme}

Check for:
MANDATORY: README.md, LICENSE, .gitignore, requirements.txt or equivalent
STRONG:    CONTRIBUTING.md, SECURITY.md, .env.example
CI/CD:     .github/workflows/, .gitlab-ci.yml, .circleci/
Git hygiene: .env committed, node_modules/, __pycache__/, merge conflict markers

Assign Infrastructure Score 0–10.
Save the Compliance Report to "${targetDir}/compliance-report.md".
`;

  const reply = await callGemini(systemPrompt, userMsg);
  console.log(reply);
  writeFile(join(targetDir, "compliance-report.md"), reply);
  console.log(paint(`\n  ✅ Report saved to compliance-report.md`, C.green));
  return reply;
}

async function runMortemInterrogator(systemPrompt, targetDir) {
  console.log(paint("\n🔎 SKILL  |  mortem-interrogator", C.magenta, C.bold));
  console.log(paint("   Five Whys systemic root cause analysis — blame the system, never the human.", C.dim));
  console.log(paint("   " + "─".repeat(58), C.dim));

  const incidentPath = join(targetDir, "incident.md");
  let incident = "";

  if (existsSync(incidentPath)) {
    incident = readFile(incidentPath);
  } else {
    console.log(paint("   ⚠️  No incident.md found — using synthesized incident from scan findings.", C.yellow));
    const autopsyPath = join(targetDir, "autopsy-report.md");
    incident = existsSync(autopsyPath)
      ? `# Synthesized Incident\n\nBased on forensic findings:\n\n${readFile(autopsyPath).slice(0, 1500)}`
      : "# Incident\n\nHardcoded credentials discovered in source repository. Developer committed an API key.\nInitial assessment: developer forgot to move key to environment variables.";

    writeFile(incidentPath, incident);
  }

  const userMsg = `
Execute the mortem-interrogator skill.

Incident report:
${incident}

Perform Five Whys analysis:
- Why 1: The immediate technical cause
- Why 2: The process failure that allowed it
- Why 3: The team/culture factor
- Why 4: The organizational policy gap
- Why 5: The systemic institutional failure

MANDATORY: Explicitly REJECT "human error", "developer forgot", "rushing" as root causes.
State: "REJECTED: [cause]. This is a symptom, not a cause."

The TRUE ROOT CAUSE must be a systemic failure — absent automated scanning,
broken review culture, missing guardrails, etc.

Issue a systemic recommendation that would make this class of failure structurally impossible.
Save verdict to "${targetDir}/systemic-finding.md".
`;

  const reply = await callGemini(systemPrompt, userMsg);
  console.log(reply);
  writeFile(join(targetDir, "systemic-finding.md"), reply);
  console.log(paint(`\n  ✅ Report saved to systemic-finding.md`, C.green));
  return reply;
}

async function runMergeRisk(systemPrompt, targetDir) {
  console.log(paint("\n🔮 SKILL  |  merge-risk", C.cyan, C.bold));
  console.log(paint("   Cross-referencing incoming changes against past systemic findings.", C.dim));
  console.log(paint("   " + "─".repeat(58), C.dim));

  const diffPath = getOrGenerateDiff(targetDir);

  if (!diffPath) {
    console.log(paint("   ℹ️  No diff available. Provide diff.txt or run in a git repo with history.", C.dim));
    return "merge-risk: skipped — no diff available.";
  }

  const diff       = readFile(diffPath).slice(0, 4000);
  const autopsyPath = join(targetDir, "autopsy-report.md");
  const systemicPath = join(targetDir, "systemic-finding.md");
  const autopsy     = existsSync(autopsyPath)  ? readFile(autopsyPath).slice(0, 1500)  : "No autopsy report yet.";
  const systemic    = existsSync(systemicPath) ? readFile(systemicPath).slice(0, 1000) : "No systemic finding yet.";

  const userMsg = `
Execute the merge-risk skill.

Incoming diff (PR changes):
${diff}

Past autopsy findings:
${autopsy}

Past systemic root causes:
${systemic}

Cross-reference the diff against known findings:
- Do changed files have previous CRITICAL findings?
- Do new changes introduce the same anti-patterns that caused past incidents?
- Are new dependencies being added without pinning?

Assign MERGE VERDICT:
- BLOCK:   Changes repeat a previously identified CRITICAL finding
- WARN:    Changes touch high-risk areas from autopsy
- CAUTION: New code follows patterns correlated with past debt
- CLEAR:   No regression risk detected

Save the Merge Risk Assessment to "${targetDir}/merge-risk-report.md".
`;

  const reply = await callGemini(systemPrompt, userMsg);
  console.log(reply);
  writeFile(join(targetDir, "merge-risk-report.md"), reply);
  console.log(paint(`\n  ✅ Report saved to merge-risk-report.md`, C.green));
  return reply;
}

// ─────────────────────────────────────────────────────────────
//  Skill menu
// ─────────────────────────────────────────────────────────────

const SKILLS = {
  "1": { name: "repo-autopsy",        label: "🔬 repo-autopsy        — Scan codebase for security anti-patterns",  fn: runRepoAutopsy      },
  "2": { name: "secret-scanner",      label: "🔑 secret-scanner      — Hunt hardcoded credentials & API keys",      fn: runSecretScanner    },
  "3": { name: "dependency-audit",    label: "📦 dependency-audit    — Audit dependency posture & lockfiles",        fn: runDependencyAudit  },
  "4": { name: "compliance-check",    label: "📋 compliance-check    — Audit project infrastructure & git hygiene", fn: runComplianceCheck  },
  "5": { name: "mortem-interrogator", label: "🔎 mortem-interrogator — Five Whys root cause analysis",              fn: runMortemInterrogator },
  "6": { name: "merge-risk",          label: "🔮 merge-risk          — Evaluate PR diff for regression risk",        fn: runMergeRisk        },
};

const SKILL_BY_NAME = Object.fromEntries(
  Object.entries(SKILLS).map(([k, v]) => [v.name, k])
);

function printMenu(targetDir) {
  const inner = 90;
  const div = "─".repeat(inner);
  console.log(`\n${paint("┌" + div + "┐", C.cyan)}`);
  const title = " CausalLoop — Skill Selection ";
  const pad = Math.max(0, inner - title.length);
  const l = Math.floor(pad / 2), r = pad - l;
  console.log(paint("│", C.cyan) + " ".repeat(l) + paint(title, C.bold, C.white) + " ".repeat(r) + paint("│", C.cyan));
  console.log(paint("├" + div + "┤", C.cyan));

  const infoLines = [
    paint(`  Target : ${targetDir}`, C.white),
    paint(`  Engine : Gemini API (Node.js runtime)`, C.dim),
    "",
    paint("  [1]", C.green)   + "  " + paint(SKILLS["1"].label, C.bold),
    paint("  [2]", C.red)     + "  " + paint(SKILLS["2"].label, C.bold),
    paint("  [3]", C.yellow)  + "  " + paint(SKILLS["3"].label, C.bold),
    paint("  [4]", C.blue)    + "  " + paint(SKILLS["4"].label, C.bold),
    paint("  [5]", C.magenta) + "  " + paint(SKILLS["5"].label, C.bold),
    paint("  [6]", C.cyan)    + "  " + paint(SKILLS["6"].label, C.bold),
    paint("  [7]", C.white)   + "  " + paint("⚡ full-investigation  — Run all 6 skills in sequence", C.bold),
    "",
    paint("  [r]", C.yellow)  + "  " + paint("🚀 remote repo         — Target a remote public GitHub URL", C.bold),
    "",
    paint("  [h]", C.dim) + "  help    " + paint("[q]", C.dim) + "  quit",
  ];

  for (const line of infoLines) {
    const visible = line.replace(/\x1b\[[0-9;]*m/g, "");
    const padding = Math.max(0, inner - visible.length - 1);
    console.log(paint("│", C.cyan) + line + " ".repeat(padding) + paint("│", C.cyan));
  }
  console.log(paint("└" + div + "┘", C.cyan));
}

// ─────────────────────────────────────────────────────────────
//  Interactive loop
// ─────────────────────────────────────────────────────────────

async function interactiveLoop(systemPrompt, targetDir) {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  const ask = (q) => new Promise((res) => rl.question(q, res));

  while (true) {
    printMenu(targetDir);
    const input = await ask(paint("\nCausalLoop> ", C.cyan, C.bold));
    const choice = input.trim().toLowerCase();

    if (!choice || choice === "h" || choice === "help") continue;
    if (choice === "q" || choice === "quit" || choice === "exit") {
      console.log(paint("\n  Exiting CausalLoop. The loop is closed.\n", C.dim));
      rl.close();
      break;
    }

    if (choice === "r" || choice === "remote") {
      const url = await ask(paint("  Enter public GitHub/GitLab URL> ", C.yellow));
      if (!url.trim()) continue;
      cleanup(); // remove previous clone if any
      try {
        targetDir = cloneRepo(url.trim());
      } catch (err) {
        console.error(paint(`  ❌ ${err.message}`, C.red));
      }
      continue;
    }

    if (choice === "7") {
      console.log(paint("\n  ⚡ Running full investigation…", C.magenta, C.bold));
      for (const key of ["1", "2", "3", "4", "5", "6"]) {
        await SKILLS[key].fn(systemPrompt, targetDir);
      }
      console.log(paint("\n  ✅ Full investigation complete.", C.green, C.bold));
      continue;
    }

    const skill = SKILLS[choice] || SKILLS[SKILL_BY_NAME[choice]];
    if (skill) {
      await skill.fn(systemPrompt, targetDir);
      console.log(paint(`\n  ✅ Skill '${skill.name}' complete.`, C.green));
    } else {
      console.log(paint(`  ❌  Unknown option: '${choice}'`, C.red));
    }
  }
}

// ─────────────────────────────────────────────────────────────
//  CLI argument parsing
// ─────────────────────────────────────────────────────────────

function parseArgs() {
  const args = process.argv.slice(2);
  const result = {
    repo:   null,
    skill:  null,
    all:    false,
    target: process.cwd(),
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--repo"   && args[i + 1]) { result.repo   = args[++i]; continue; }
    if (args[i] === "--skill"  && args[i + 1]) { result.skill  = args[++i]; continue; }
    if (args[i] === "--target" && args[i + 1]) { result.target = args[++i]; continue; }
    if (args[i] === "--all")   { result.all   = true; continue; }
  }

  return result;
}

// ─────────────────────────────────────────────────────────────
//  Main
// ─────────────────────────────────────────────────────────────

async function main() {
  process.stdout.write(HEADER);

  const opts = parseArgs();
  let targetDir = opts.target;

  if (opts.repo) {
    try {
      targetDir = cloneRepo(opts.repo);
    } catch(err) {
      console.error(paint(`❌  ${err.message}`, C.red));
      cleanup();
      process.exit(1);
    }
  }

  console.log(paint("  Loading agent identity (SOUL.md + RULES.md + skills)…", C.dim));
  const systemPrompt = loadIdentity();
  console.log(paint("  ✅ Agent ready.\n", C.green));

  try {
    if (opts.skill) {
      const key = SKILL_BY_NAME[opts.skill];
      if (!key) {
        console.error(paint(`❌  Unknown skill: '${opts.skill}'`, C.red));
        console.error("Available: " + Object.values(SKILLS).map(s => s.name).join(", "));
        process.exit(1);
      }
      await SKILLS[key].fn(systemPrompt, targetDir);
    } else if (opts.all) {
      console.log(paint("  ⚡ Running all 6 skills…\n", C.magenta, C.bold));
      for (const key of ["1", "2", "3", "4", "5", "6"]) {
        await SKILLS[key].fn(systemPrompt, targetDir);
      }
      console.log(paint("\n  ✅ Full investigation complete.", C.green, C.bold));
    } else {
      await interactiveLoop(systemPrompt, targetDir);
    }
  } finally {
    cleanup();
  }
}

main().catch((err) => {
  console.error(paint(`\n❌  Fatal error: ${err.message}`, C.red));
  cleanup();
  process.exit(1);
});
