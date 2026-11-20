# klk-create-stories

See `sdd-overview.md` for artifact layout and gates before using this file.
Tests already exist by this point (written by `klk-create-tests`) — this
command does **not** invent new acceptance criteria. It breaks the feature
into implementation-sized tasks and cites, per story, which already-written
AC/tests it's responsible for turning green.

**Input**: `docs/sdd/<feature-slug>/tests.md`, plus `spec.md`/`tech-spec.md`
for context.
**Output**: `docs/sdd/<feature-slug>/stories.md`, each story already at
status `Ready for Implementation`.

1. Read `tech-spec.md` for its `AC-*` list, then run
   `python3 scripts/sdd_check.py gate-tests docs/sdd/<feature-slug>/tests.md --acs <all AC-IDs>`.
   **Refuse to proceed on exit 1** — name each `AC-*` with no recorded test
   and stop. Don't write a story against an AC that was never actually
   turned into a test.
2. Decompose the `AC-*` items into independently implementable user
   stories — one story can cover one AC, or several AC that ship together
   naturally. Every `AC-*` must be covered by at least one story; every
   story must cite the `REQ-*`/`TS-*`/`AC-*` ID(s) it covers **and** the
   test name(s) from `tests.md` that verify them.
3. Fill this template per story:

   ```markdown
   ## US-001: <short title>
   - **Covers**: AC-1, AC-2 (REQ-001/TS-001)
   - **Tests**: `<file path>::<test name>`, `<file path>::<test name>`
   - **Status**: Ready for Implementation
   - **Priority**: P1 | P2 | P3
   - **Story**: As a <role>, I want <capability>, so that <benefit>.
   - **Acceptance criteria**:
     - **AC-1**: <restated verbatim from tech-spec.md — not reworded, so it
       can't quietly drift from the test it names>
     - **AC-2**: <restated verbatim from tech-spec.md>
   ```

   The `## Acceptance criteria` bullets here are a restatement for backlog
   readability, not a new authoring step — if a story's AC text doesn't
   match `tech-spec.md`'s wording for that ID, that's a bug in this
   command's output, not a deliberate rephrasing.
4. Set every new story's `Status` to `Ready for Implementation` directly —
   there is no earlier status to advance from, since the tests this story
   depends on already exist and are already red. Order stories by priority,
   P1 first. Don't invent stories that don't trace back to an `AC-*`.

Report back the full list of story IDs, each one's covered AC/test names,
and flag any `AC-*` that didn't end up covered by a story — that's a gap,
not a silent omission.
