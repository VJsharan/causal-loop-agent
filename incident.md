# Incident Report: INC-2026-04

**Title:** Unauthorized Access and Remote Code Execution
**Date:** 2026-04-06

**Description:**
A malicious actor gained full administrative access to the production system. Forensic logs indicate that they bypassed normal authentication. They logged in using hardcoded `admin` credentials, and then exploited an unsafe `eval()` call in the authentication module to execute remote Python code on the server.

**Proximate Cause:**
A developer accidentally left test credentials in production code and used a dangerous string evaluation function. The developer was rushing to meet a deadline. Human error and lack of QA oversight.

**Immediate Resolution:**
Credentials have been rotated. The script was patched to remove the `eval()` call and hardcoded passwords.
