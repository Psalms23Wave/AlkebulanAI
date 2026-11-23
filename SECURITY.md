# Security Policy

## Supported versions

The current major release of Alkebulan AI receives security updates.
Older versions are supported on a best-effort basis.

| Version | Status           |
|---------|------------------|
| 1.x     | Active support   |

## Reporting a vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

If you believe you have found a security vulnerability in Alkebulan AI,
please report it privately through the Psalms23Wave contact form:

> **[psalms23wave.com/contact](https://www.psalms23wave.com/contact)**
>
> **Subject:** *"Security report — Alkebulan AI"*

Using the form keeps the disclosure private and routes it directly
to the maintainers. **Do not** discuss the vulnerability in a public
GitHub issue, pull request, or social-media post until a fix has
been published.

Please include:

- A description of the vulnerability and its potential impact.
- Steps to reproduce the issue (minimum reproducer, if possible).
- The affected version(s) and commit hash.
- Any suggested mitigations you've identified.
- Whether you wish to be credited in the advisory (and how).

## What to expect

- **Acknowledgement:** within **3 business days**.
- **Initial assessment:** within **7 business days**, including
  severity classification and a rough fix timeline.
- **Fix and disclosure:** co-ordinated disclosure with the reporter;
  a public advisory is published once a fix is available and a
  reasonable patch-adoption window has passed.
- **Credit:** reporters who wish to be named will be credited in
  the advisory (unless you request anonymity).

## Scope

In scope:

- The `tokenizer/` package.
- The `sekan_algorithm/` package.
- Example scripts and notebooks distributed in this repository.
- Model artefacts distributed under `tokenizer/` and `packages/ablt/`.

Out of scope:

- Third-party dependencies (report those upstream, e.g. to
  `sentencepiece`, `pytorch`, `transformers`).
- Issues requiring physical access to a user's machine.
- Social-engineering attacks.

## Bug bounties

Psalms23Wave LLC does not currently run a paid bug-bounty programme.
We will acknowledge and credit security researchers in advisories
and in the project's CONTRIBUTORS.md.

---

© 2025 Psalms23Wave LLC.
