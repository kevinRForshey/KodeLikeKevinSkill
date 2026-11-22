# klk-create-tests

See `sdd-overview.md` for artifact layout and gates before using this file.
This command writes **tests only** — the red half of red-green TDD — and
establishes the feature's Definition of Done. Never write production/
implementation code here; that's `klk-implement-stories`. Never write
stories here either; that's `klk-create-stories`, which runs *after* this.

**Input**: an approved `docs/sdd/<feature-slug>/tech-spec.md`.
**Output**: failing tests in the project's real test project(s), and
`docs/sdd/<feature-slug>/tests.md` recording them.

1. Run `python3 scripts/sdd_check.py gate-clarifications docs/sdd/<feature-slug>/tech-spec.md`
   first. **Refuse to proceed on exit 1** — name each listed item exactly,
   and stop. Don't write a test against an unresolved ambiguity. Then read
   `tech-spec.md` itself for its `AC-*` list.
2. Use whatever test framework the target repo already has installed
   (xUnit, MSTest, Jest, unittest, etc.) if one exists — never introduce a
   second one. Only when none exists yet: default to xUnit for C# (the
   `dotnet-testing` skill), or to the idiomatic choice in the
   `kodelikekevin` skill's language reference files for non-.NET work.
3. Write one test (or a tightly-grouped set) per `AC-*` in `tech-spec.md`.
   Name or tag each test so it traces back to its AC, e.g.
   `AC003_RejectsExpiredToken` or an `[AC-003]` tag/comment — whatever the
   project's existing test-naming convention favors, extended with the AC
   ID. Cover both the AC's happy path and any guard/error case implied by
   it. These tests also count toward `ai-governance`'s 90% coverage floor
   and must clear its trivial-assertion screening (a test that only proves
   a line ran, without asserting real behavior, doesn't count) — write
   accordingly, don't pad the number.
4. **Run the new tests and confirm they fail** (red) because the feature
   doesn't exist yet. If a test unexpectedly passes, don't count it as
   covered — report it: either the feature already exists, or the test
   itself doesn't actually exercise the behavior.
5. Write `docs/sdd/<feature-slug>/tests.md`:

   ```markdown
   # <Feature Name> — Tests (Definition of Done)

   Definition of done: every test below passes.

   - **AC-1** [REQ-00N/TS-00N]: <the AC text, copied from tech-spec.md>
     - Test: `<file path>::<test name>` — red
   - **AC-2** [REQ-00N/TS-00N]: <the AC text, copied from tech-spec.md>
     - Test: `<file path>::<test name>` — red
     - Test: `<file path>::<test name>` — red
   ```

   List every test covering an AC under it (an AC can have more than one).
   This file is written once, as a snapshot proving the tests exist and
   were observed red — it is not rewritten as tests later go green (that's
   tracked per-story in `stories.md`, not here).
6. Run `python3 scripts/sdd_check.py gate-tests docs/sdd/<feature-slug>/tests.md --acs <all AC-IDs>`
   and report its result directly — confirms every AC actually has a
   recorded test entry, not just a claim.

Report back which AC IDs got tests, their file paths, and confirmation that
each new test was observed failing before this command finished. This
`tests.md` is what `klk-create-stories` reads next, and what `klk-run-qa`
ultimately checks the implementation against.
