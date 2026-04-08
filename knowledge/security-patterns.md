# Security Patterns Reference

This knowledge base helps CausalLoop recognize and classify security anti-patterns during forensic analysis.

## Credential Patterns

### Hardcoded Secrets
**Detection keywords:** `password`, `secret`, `api_key`, `token`, `passwd`, `pwd`
**Risk:** CRITICAL — Hardcoded credentials are the single most common cause of production breaches.
**Causal chain:** Developer shortcuts under deadline pressure → no pre-commit secret scanning → credential leaked in git history (permanent even after deletion) → attackers mine GitHub for these patterns automatically.

### Private Key Material
**Detection patterns:** `BEGIN RSA PRIVATE KEY`, `BEGIN EC PRIVATE KEY`, `BEGIN OPENSSH PRIVATE KEY`
**Risk:** CRITICAL — Full system compromise is immediate.

### Cloud Provider Keys
**Detection patterns:**
- AWS: `AKIA[0-9A-Z]{16}` (Access Key ID format)
- GitHub: `ghp_[a-zA-Z0-9]{36}` (Personal Access Token)
- Slack: `xoxb-[0-9]{11}-[0-9]{11}-[a-zA-Z0-9]{24}` (Bot Token)
- Stripe: `sk_live_[a-zA-Z0-9]{24}` (Secret Key)
**Risk:** CRITICAL — Automated scanners find these within minutes of a public push.

---

## Dangerous Function Patterns

### Arbitrary Code Execution
**Detection:** `eval(`, `exec(`, `os.system(`, `subprocess.call(`, `__import__(`
**Risk:** CRITICAL — Any of these accepting user input creates Remote Code Execution vulnerability.
**Causal chain:** Developer needed dynamic execution → chose eval() as "quickest path" → no input sanitization → attacker injects payload → full server compromise.

### SQL Injection
**Detection:** String concatenation into SQL queries — `"SELECT * FROM users WHERE id = " + userId`
**Risk:** CRITICAL (OWASP A03:2021)
**Safe alternative:** Parameterized queries — `cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))`

### Deserialization
**Detection:** `pickle.loads(`, `yaml.load(` (without Loader), `marshal.loads(`
**Risk:** ELEVATED — Deserializing untrusted data can lead to RCE.

---

## Technical Debt Signals

### Acknowledged Debt
**Detection keywords:** `TODO`, `FIXME`, `HACK`, `TEMP`, `XXX`, `WORKAROUND`
**Meaning:** Developer was aware of the shortcut. These are "honorable debts" — acknowledged but unpaid.
**Severity:** DEPRESSINGLY-PREDICTABLE — The commit message "FIXME: remove before production" that ships to production is the canonical example.

### Deadline Debt
**Detection keywords:** `quick`, `for now`, `just to ship`, `temporary`, `we'll fix this`, `out of time`
**Causal chain:** Deadline pressure → conscious corner-cutting → "temporary" becomes permanent → accumulates until a crisis forces a rewrite.

---

## Dependency Risk Patterns

### Unpinned Dependencies
**Detection:** Version specifiers like `>=1.0`, `*`, or missing versions in requirements.txt
**Risk:** ELEVATED — A minor dependency update can silently break production.
**Safe pattern:** Pin exact versions in `requirements.txt` and use a lockfile.

### Outdated Lockfiles
**Detection:** `package-lock.json` or `requirements.txt` not updated in 6+ months alongside active development.
**Risk:** ELEVATED — Vulnerable packages accumulate silently.

### Missing Lockfile
**Detection:** `requirements.txt` or `package.json` present without corresponding lockfile.
**Risk:** ELEVATED — Reproducible builds are impossible; CI and prod may install different versions.

---

## Configuration Security

### Debug Mode in Production
**Detection:** `DEBUG=True`, `debug=true`, `NODE_ENV=development` in deployed configs
**Risk:** ELEVATED — Debug mode exposes stack traces, internal paths, and sometimes config values to users.

### Permissive CORS
**Detection:** `Access-Control-Allow-Origin: *`, `cors({ origin: '*' })`
**Risk:** ELEVATED — Allows any website to make authenticated requests on behalf of your users.

### Missing HTTPS Enforcement
**Detection:** HTTP URLs in production configs, missing HSTS headers
**Risk:** ELEVATED — Traffic is interceptable in clear text.
