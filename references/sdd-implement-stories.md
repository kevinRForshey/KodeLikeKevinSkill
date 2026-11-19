# klk-implement-stories

See `sdd-overview.md` for artifact layout and gates before using this file.

**Input**: stories in `stories.md` with status `Tests Written` (tests
exist and are currently red).
**Output**: production code that turns each targeted story's tests green;
each story's status updated to `Implemented`.

1. Read `stories.md` and the failing tests for the story (or stories) to
   implement. **Refuse a story that isn't `Tests Written`** — name it and
   point at `klk-create-qa` rather than implementing against no tests or
   against tests you write yourself in this same step.
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
   but **don't mark the story `Passing`**. Update its status only to
   `Implemented`; `klk-run-qa` is the independent gate that confirms
   `Passing` with its own full run.
6. If implementing one story surfaces a needed change to an earlier story's
   already-passing tests, stop and report the conflict rather than quietly
   editing both to agree.

Report back which story IDs you implemented, the files touched, and that
their tests are observed passing locally — then hand off to `klk-run-qa` for
the independent check.
