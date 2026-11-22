# klk-ship

See `sdd-overview.md` for artifact layout and gates before using this file.
This is the pipeline's closing step: it doesn't write or fix code, and it
never commits or pushes. It verifies the feature is actually ready, drafts
a traceable PR description, and stages the diff for the user's own review
and commit.

**Input**: `stories.md` with its stories at `Passing` (typically after
`klk-run-qa`), plus `spec.md`/`tech-spec.md` for traceability.
**Output**: `docs/sdd/<feature-slug>/pr-description.md`; the feature's
changed files staged (`git add`) but not committed.

1. Run `python3 scripts/sdd_check.py gate-ship docs/sdd/<feature-slug>/tech-spec.md docs/sdd/<feature-slug>/stories.md`
   — omit `--ids` for a whole-feature ship (the default; every `AC-*` in
   `tech-spec.md` must be covered by a story and every story must be
   `Passing`), or pass `--ids <US-ID> [US-ID ...]` to ship a subset of an
   in-progress feature's stories (skips the whole-feature AC-closure check,
   since the untargeted stories are deliberately out of scope for this
   run). **Refuse to proceed on exit 1** — name exactly which AC has no
   story or which story isn't `Passing`, point at `klk-create-stories` (an
   uncovered AC) or `klk-implement-stories`/`klk-run-qa` (a story not yet
   `Passing`), and stop. Never draft a PR for a feature that isn't actually
   done.
2. Read `spec.md` (for `REQ-*`/`SC-*`), `tech-spec.md` (for `TS-*`/`AC-*`
   and any `## Non-functional notes`), and `stories.md` (for the `US-*`
   IDs and their `Tests:` lines) to assemble traceability, then run
   `git status` and `git diff --stat` (read-only) to see what actually
   changed in the working tree.
3. Write `docs/sdd/<feature-slug>/pr-description.md`:

   ```markdown
   # <Feature Name>

   ## Summary
   <One or two sentences: what this feature does, from spec.md's Purpose
   & Scope — not a restatement of every REQ/AC.>

   ## Closes
   - REQ-001, REQ-002 (spec.md)
   - US-001, US-002 (stories.md)

   ## Test plan
   - AC-1 — `<test name(s) from tests.md/stories.md>` — passing
   - AC-2 — `<test name(s)>` — passing

   ## Notes
   <Only if tech-spec.md has a `## Non-functional notes` section worth
   surfacing to a reviewer. Omit otherwise.>
   ```

   Keep the Summary factual and scoped to what this feature actually does
   — don't restate the full spec/tech-spec/stories content here; that's
   what the linked artifacts are for.
4. Cross-check `git diff --stat`'s file list against what the shipped
   stories claim to have touched. If the working tree has unrelated
   uncommitted changes, or a story claims a file that `git diff` doesn't
   show as changed, flag the discrepancy and ask rather than silently
   including or excluding it.
5. Stage the feature's changed files with `git add` — staging doesn't
   require asking, per this skill's `## Version Control Policy`. **Never
   run `git commit` or `git push` here**, regardless of how clean the gate
   result looked; those still require the user's explicit go-ahead in the
   current conversation.

Report back the PR description content, which files got staged, and the
gate result from step 1. Tell the user the draft is ready for their review
and that committing/pushing is still their call to make.
