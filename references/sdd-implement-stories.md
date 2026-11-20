# klk-implement-stories

See `sdd-overview.md` for artifact layout and gates before using this file.

**Input**: stories in `stories.md` with status `Ready for Implementation`
(their tests already exist, per `tests.md`, and are currently red).
**Output**: production code that turns each targeted story's tests green;
each story's status updated to `Implemented`.

1. Run `python3 scripts/sdd_check.py gate-stories docs/sdd/<feature-slug>/stories.md --ids <target US-IDs> --status "Ready for Implementation"`.
   **Refuse any story the script flags** — name it and point at
   `klk-create-tests`/`klk-create-stories` rather than implementing against
   no tests or against tests written yourself in this same step. Then read
   `stories.md` (its `Tests:` line) and the failing tests themselves for
   the story (or stories) to implement.
2. Implement the minimum real production code that satisfies the story's
   acceptance criteria and makes its tests pass — following this skill's
   `## Core principles` (KISS/SOLID/YAGNI) and the relevant
   `references/*-practices.md` file for naming, component, and data-access
   conventions in the language in play.
3. **Never edit or weaken a test to make it pass.** If a test appears wrong
   — contradicts the story's acceptance criteria or the spec — stop and
   flag the specific discrepancy rather than changing the test unilaterally.
4. Apply this skill's `## Documentation & attribution` rules to any code
   touched here: doc comments + OpenAPI annotations for a public API
   surface change, a `docs/user/` entry for a user-facing feature, and
   attribution comments for anything adapted from an identifiable external
   source.
5. Run the story's tests yourself as you go (standard red-green-refactor) —
   but **don't mark the story `Passing`**. Update its status only with
   `python3 scripts/sdd_check.py set-status docs/sdd/<feature-slug>/stories.md <US-ID> "Implemented"`;
   `klk-run-qa` is the independent gate that confirms `Passing` with its own
   full run.
6. If implementing one story surfaces a needed change to an earlier story's
   already-passing tests, stop and report the conflict rather than quietly
   editing both to agree.

Report back which story IDs you implemented, the files touched, and that
their tests are observed passing locally — then hand off to `klk-run-qa` for
the independent check.
