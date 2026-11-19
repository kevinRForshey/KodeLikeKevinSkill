# klk-create-qa

See `sdd-overview.md` for artifact layout and gates before using this file.
This command writes **tests only** — the red half of red-green TDD. Never
write production/implementation code here; that's `klk-implement-stories`.

**Input**: stories in `stories.md` with status `Draft` or `Ready for QA`
and at least one acceptance criterion each.
**Output**: failing tests in the project's real test project(s); each
covered story's status updated to `Tests Written`.

1. Read `stories.md`. For each story you're covering, **refuse it and name
   the gap** if it has no acceptance criteria — don't write a test for a
   criterion that doesn't exist.
2. Use whatever test framework the target repo already has installed
   (xUnit, MSTest, Jest, unittest, etc.) if one exists — never introduce a
   second one. Only when none exists yet, default to the idiomatic choice
   per this skill's `## Testing` section and the matching
   `references/*-practices.md` file: xUnit (C#), Vitest + React Testing
   Library (TS/JS/React), pytest (Python). Put tests in the project's
   existing test project/folder — don't create a parallel test location
   under `docs/sdd/`.
3. Write one test (or a tightly-grouped set) per acceptance criterion.
   Name or tag each test so it traces back to its story, e.g.
   `US003_AC1_RejectsExpiredToken` or a `[US-003]` tag/comment — whatever
   the project's existing test-naming convention favors, extended with the
   story ID.
4. Cover both the AC's happy path and any guard/error case implied by it —
   same bar as this skill's general `## Testing` rule. For .NET/C#, React,
   Python, or TypeScript, these tests also count toward `ai-governance`'s
   90% coverage floor and must clear its trivial-assertion screening (a
   test that only proves a line ran, without asserting real behavior,
   doesn't count) — write accordingly, don't pad the number.
5. **Run the new tests and confirm they fail** (red) because the feature
   doesn't exist yet. If a test unexpectedly passes, don't count it as
   covered — report it: either the feature already exists, or the test
   itself doesn't actually exercise the behavior.
6. Update each covered story's `Status` in `stories.md` to `Tests Written`.
   Leave stories you didn't cover this run at their current status.

Report back which story IDs got tests, their file paths, and confirmation
that each new test was observed failing before this command finished.
