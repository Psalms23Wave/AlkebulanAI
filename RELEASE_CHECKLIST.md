<!--
Copyright (c) 2025 Mathew Sekanjako and Psalms23Wave LLC.
Licensed under the Apache License, Version 2.0.
-->

# Release Checklist — Alkebulan Bantu Language Tokenizer

A one-page safety net for the first push to
[`github.com/Psalms23Wave/AlkebulanAI`](https://github.com/Psalms23Wave/AlkebulanAI).

Run the checks in order. Do **not** flip the repo to **Public** until
every box is ticked.

---

## 0. Recommended publish strategy

Start the repo as **Private**, push, review on GitHub in the browser,
then flip to **Public**. This gives you a last safety net you can't
get any other way.

```
Create repo (Private) → git push → review on github.com → flip to Public
```

---

## 1. Local safety sweep (do this before `git add`)

Run these from inside `Alkebulan Bantu Language Tokenizer Version 1/`:

```bash
# 1. Nothing sensitive hiding in the tree?
find . -type f \( -name "*.key" -o -name "*.pem" -o -name ".env" \
                 -o -name "*secret*" -o -name "*token*" \
                 -o -name "credentials*" \) -not -path "./.git/*"
# (expected output: nothing)

# 2. No OS junk?
find . -name ".DS_Store" -o -name "Thumbs.db" -not -path "./.git/*"
# (expected output: nothing — .gitignore will block these anyway)

# 3. No Python cache?
find . -type d -name "__pycache__" -o -name ".ipynb_checkpoints"
# (expected output: nothing — .gitignore will block these anyway)

# 4. No giant files that don't belong in git?
find . -type f -size +50M -not -path "./.git/*"
# (expected output: at most the luganda_spm.model and ablt_v1_tokenizer.pkl —
#  those are supposed to be there)
```

If any of those return unexpected results, delete or `.gitignore`
them **before** you commit.

---

## 2. Documentation sanity check

- [ ] `README.md` — logo renders, all badges point to real URLs,
      **no email addresses** appear, only the contact form link.
- [ ] `LICENSE` — Apache 2.0 full text, copyright line names
      **Mathew Sekanjako and Psalms23Wave LLC, 2025**.
- [ ] `NOTICE` — present, names Mathew Sekanjako as inventor.
- [ ] `CONTRIBUTING.md`, `CLA.md`, `CODE_OF_CONDUCT.md`,
      `GOVERNANCE.md`, `MAINTAINERS.md`, `CONTRIBUTORS.md`,
      `SECURITY.md`, `TRADEMARK.md`, `COMMERCIAL.md`,
      `LICENSING.md`, `ATTRIBUTION.md` — all present.
- [ ] `docs/ADDING_A_LANGUAGE.md` — present.
- [ ] `.github/ISSUE_TEMPLATE/*` and `.github/PULL_REQUEST_TEMPLATE.md`
      — present.

---

## 3. First push

```bash
cd "Alkebulan AI/Alkebulan Bantu Language Tokenizer Version 1"

git init
git add .
git status                                   # eyeball the file list
git commit -m "Initial public release of Alkebulan Bantu Language Tokenizer v1

- ABLT tokenizer (SentencePiece Unigram, vocab 5,795)
- Sekan algorithm (Simpson-rule optimizer + attention)
- Luganda proof-of-concept + validation metrics
- Full open-source governance: Apache 2.0, CLA, CoC, BDFL"

git branch -M main
git remote add origin https://github.com/Psalms23Wave/AlkebulanAI.git
git push -u origin main
```

If prompted for credentials, use a **GitHub Personal Access Token**
(classic or fine-grained), not your password.

---

## 4. On-GitHub review (still Private)

Open the repo in the browser and check:

- [ ] README renders correctly, logo displays at the top, all
      screenshots load under "Screenshots from the notebooks".
- [ ] `LICENSE` shows up as "Apache-2.0" in the sidebar.
- [ ] `CODE_OF_CONDUCT.md` is auto-detected by GitHub (sidebar badge).
- [ ] `SECURITY.md` is auto-detected (Security tab).
- [ ] **Insights → Community Standards** — all green ticks.
- [ ] The file tree matches the layout described in the README.
- [ ] Issue templates appear when you click *"New issue"*.
- [ ] PR template appears when you open a test PR.

Fix anything that looks off. Push the fixes. Re-review.

---

## 5. Repository settings (Settings tab)

- [ ] **General → Features:** enable **Issues** and **Discussions**.
- [ ] **General → Features:** disable **Wikis** (keep docs in-repo).
- [ ] **General → Pull Requests:** enable *"Automatically delete
      head branches"* and *"Allow squash merging"* (disable merge
      commits if you prefer a linear history).
- [ ] **Branches:** add a protection rule for `main`:
      - Require pull request before merging.
      - Require 1 approval (from a maintainer).
      - Require status checks (once CI is added).
      - Do not allow force pushes.
- [ ] **Security → Code security:** enable
      **Dependabot alerts**, **Dependabot security updates**,
      and **Secret scanning**.
- [ ] **Security → Code security:** enable
      **Private vulnerability reporting** (so `SECURITY.md`
      routes correctly).
- [ ] **Moderation → Code of conduct:** link `CODE_OF_CONDUCT.md`.

---

## 6. About box (right-hand sidebar of the repo front page)

- **Description:**
  *"The first morphologically-aware tokenizer for Luganda, built
  from scratch. Powered by the Sekan algorithm — a Simpson-rule
  optimizer invented for agglutinative African languages.
  Open-source (Apache 2.0). By Psalms23Wave LLC."*
- **Website:** `https://www.psalms23wave.com`
- **Topics (tags):** `tokenizer`, `nlp`, `african-languages`,
  `luganda`, `bantu`, `sentencepiece`, `mistral`, `low-resource-languages`,
  `morphology`, `optimizer`, `simpsons-rule`, `open-source`,
  `apache-2-0`, `psalms23wave`, `alkebulan-ai`, `alkebulanai`.

---

## 7. Flip to Public

Only when every box above is ticked:

**Settings → General → Danger Zone → Change repository visibility →
Make public.**

GitHub will ask you to type the repo name to confirm. Do it.

---

## 8. Announce

Post the launch across the channels you already own:

- **Psalms23Wave site** — add a "Projects" entry linking to the repo.
- **Hugging Face** — update the model card on
  `Psalms23Wave/Alkebulan-AI` to link to the GitHub repo and to
  mention Apache 2.0.
- **GitHub org** (`github.com/Psalms23Wave`) — pin the repo.
- **LinkedIn / X / personal portfolio** — announce with the Sekan
  thesis headline and the *psalms23wave.com/contact* CTA.

---

## 9. Post-launch (week 1)

- [ ] Enable **GitHub Sponsors** for the org (optional but useful).
- [ ] Add a CITATION file in the next release for academic attribution.
- [ ] Set up GitHub Actions CI: lint, `ast.parse`, unit tests.
- [ ] Add a minimal `pyproject.toml` + publish the Python package to
      PyPI as `alkebulan-tokenizer` (reserves the name).
- [ ] Watch the **Issues** tab daily for the first two weeks.

---

**That's it. Open-sourcing is a one-time event — doing it carefully
the first time pays off for the life of the project.**

— Mathew Sekanjako, Founder, Psalms23Wave LLC
