# Project Governance

This document describes how decisions are made in the Alkebulan AI
project.

---

## 1. Overview

Alkebulan AI is a **company-stewarded open-source project**. The
code is Apache 2.0 and open to community contribution; the project
as a whole is shepherded by Psalms23Wave LLC and its founder,
Mathew Sekanjako.

The governance model is **BDFL with a Maintainer Council** — a
common and battle-tested structure for research-led OSS projects
such as Python, Linux, and PyTorch (early era).

---

## 2. Roles

### 2.1 Benevolent Dictator For Life (BDFL)

- **Mathew Sekanjako** — Founder and Project Lead.
- Final authority on technical direction, release cadence, and the
  Marks (see [`TRADEMARK.md`](./TRADEMARK.md)).
- Sole signing authority for commercial licenses on behalf of
  Psalms23Wave LLC.
- Maintains veto power over any change that materially alters the
  project's scope or mission.

### 2.2 Maintainer Council

- A group of trusted long-term contributors listed in
  [`MAINTAINERS.md`](./MAINTAINERS.md).
- Empowered to triage issues, review and merge pull requests,
  cut releases, and represent the project publicly.
- Appointed and removed by the BDFL, typically on the basis of
  demonstrated sustained contribution.
- Responsible for the day-to-day running of the project.

### 2.3 Language Stewards

- Each supported language has at least one **Language Steward** —
  usually the primary author of that language's rule pack.
- Responsible for the linguistic accuracy of their rule pack,
  for reviewing PRs that touch it, and for keeping the language
  documentation up-to-date.
- Listed alongside their language in [`MAINTAINERS.md`](./MAINTAINERS.md).

### 2.4 Contributors

- Anyone who has had a pull request merged.
- Listed in [`CONTRIBUTORS.md`](./CONTRIBUTORS.md).
- Have voice in discussions and issues.

---

## 3. Decision-making

### 3.1 Day-to-day decisions

- **Bug fixes, docs, small features:** any Maintainer can merge
  after a review.
- **New language rule packs:** the relevant Language Steward (or,
  if there is none yet, any Maintainer) plus one other Maintainer
  review; BDFL is notified but does not block routine additions.
- **Large refactors, API changes, new dependencies:** discussed in
  a GitHub issue, require BDFL approval before merge.
- **Changes to the Sekan algorithm itself:** require BDFL approval.
  Sekan is the mathematical engine of the project and changes
  are reviewed rigorously.

### 3.2 Strategic decisions

Reserved to the BDFL:

- Choice of license and any change thereto.
- Any change to the Marks or TRADEMARK policy.
- Signing of commercial licenses.
- Appointment / removal of Maintainers.
- Publication of papers or academic materials under the project name.
- Partnerships, grants, and sponsorships.

### 3.3 Disputes

If contributors disagree, the path is:

1. Discuss in the relevant issue or PR.
2. If unresolved, a Maintainer calls a decision.
3. If the decision is contested, the BDFL rules. The ruling is final.

This is deliberately simple. The project will stay this way while
it is small. We will revisit the governance model once there is a
sustained community of many independent contributors.

---

## 4. Release process

- Releases follow **semantic versioning**: `MAJOR.MINOR.PATCH`.
  - `MAJOR` — incompatible API changes.
  - `MINOR` — new languages or new features that are backwards-compatible.
  - `PATCH` — bug fixes only.
- Each release has a **changelog entry** listing new features,
  new languages, bug fixes, and contributors since the last release.
- Releases are cut by a Maintainer, tagged in Git, and published to
  Hugging Face / GitHub Releases.
- Security patches (see [`SECURITY.md`](./SECURITY.md)) are
  **always backported** to the latest two minor releases.

---

## 5. Funding

Psalms23Wave LLC funds the project today via commercial licensing
(see [`COMMERCIAL.md`](./COMMERCIAL.md)) and the Founder's time.

Future funding sources we will pursue:

- Grants from foundations focused on African tech, language
  preservation, or low-resource NLP.
- Sponsorship by companies using the Project in production.
- Consulting engagements for enterprise rule-pack development.

All funds received are reinvested into extending the project to
new languages and supporting community contributors.

---

## 6. Amendments

This governance document can be amended by the BDFL, with any
material change announced in a GitHub issue for community feedback
before being merged.

---

© 2025 Psalms23Wave LLC.
