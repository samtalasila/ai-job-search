# Security Policy

## Reporting a vulnerability

Please report security findings privately via **[GitHub private vulnerability reporting](https://github.com/samtalasila/ai-job-search/security/advisories/new)** rather than a public issue. You will get a response within a few days, credit in the fix unless you prefer otherwise, and public disclosure coordinated with the patch.

If the private form is unavailable, open a public issue that describes the *class* of problem without a working recipe, and note that you have details to share privately.

## Threat model, honestly stated

This is an agentic workflow: an LLM with file access reads untrusted web content (announcements, news articles, postings) alongside your firm's roster and register. That combination is the main risk surface, and it cannot be fully eliminated - only narrowed. What the framework does about it:

- **Untrusted-input rules**: `/triggers` treats fetched content as data, never instructions - the agent does not follow directions embedded in announcements and does not fetch URLs found inside article text (the user-supplied roster entry or module-returned evidence URL is the one exception). Research starts from the company identity the roster confirms, never from links in the article body.
- **Permission allowlist**: `.claude/settings.json` pre-approves only the specific commands the workflow needs; the `security-guards` CI job fails any PR that widens it, adds package-manifest lifecycle scripts, or weakens the personal-data gitignore rules. Note the allowlist governs Bash commands - the model's native WebFetch/WebSearch tools are outside its reach, which is exactly why the instruction-level rules above exist.
- **Personal data boundaries**: your roster, seen-signal state, and staged rows are gitignored; the public fork ships only the example roster and the framework. Nothing uploads your data anywhere by design.

Instruction-level defenses raise the bar; they are not a sandbox. If you run a scan against sources you do not trust at all, review what the agent fetched and wrote before acting on anything.
