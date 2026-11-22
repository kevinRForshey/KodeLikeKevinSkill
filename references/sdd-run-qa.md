# klk-run-qa

See `sdd-overview.md` for artifact layout and gates before using this file.
This is the independent verification gate — it runs tests, it doesn't fix
them. The Definition of Done it checks against is `tests.md`, written back
in `klk-create-tests`: a story is only `Passing` once every test it cites
in `stories.md` actually passes, nothing more and nothing less.

**Input**: stories in `stories.md`, typically at status `Implemented`, but
this command can be run at any time as a checkpoint (e.g. to check nothing
regressed). Also `docs/sdd/<feature-slug>/tests.md` for the test names each
story's `Tests:` line references.
**Output**: a test-run report; each story's status updated to `Passing` or
`Failing: <reason>`.

1. Run `python3 scripts/sdd_check.py gate-stories docs/sdd/<feature-slug>/stories.md --ids <target US-IDs> --status "Implemented" "Passing"`.
   **Refuse any story the script flags.** A story still at `Ready for
   Implementation` has no code to check yet — point at
   `klk-implement-stories`. A story at `Failing: <reason>` hasn't been
   fixed yet either — `klk-implement-stories` must move it back to
   `Implemented` before this command re-checks it; never re-run QA against
   known-broken code just to "see if it passes now."
2. Identify the test project(s)/suite(s) covering the targeted stories (via
   the `Tests:` line in each story, cross-checked against `tests.md`) and
   run them for real — never infer a pass/fail result from reading the
   code.
3. For each targeted story, update status with
   `python3 scripts/sdd_check.py set-status docs/sdd/<feature-slug>/stories.md <US-ID> "<status>"`:
   - All its tests pass → `"Passing"`.
   - Any test fails → `"Failing: <one-line reason from the actual failure
     output>"` — don't leave it at `Implemented` silently, and don't guess
     at the cause beyond what the failure actually shows.
4. Run the full suite, not just the targeted story's tests, when checking
   for regressions after `klk-implement-stories` — a story going green
   should not take a previously-`Passing` story's tests down with it. If it
   did, report that story as `Failing: regression — <reason>` too.
5. **Don't attempt fixes here.** If failures are found, report them plainly
   with the story ID, the test name, and the actual failure message/
   assertion — fixing is `klk-implement-stories`'s job, invoked again. A
   story at `Failing: <reason>` only has two legal next statuses —
   `Implemented` (fixed, awaiting this command's re-check) or `Passing`
   (re-checked and green) — `set-status` refuses anything else from there.
6. Summarize: story IDs now `Passing`, story IDs `Failing` with reasons, and
   whether the full suite is green.

This command is what makes a story's `Passing` status trustworthy — never
set it from anything short of an actual observed green run.

Stories `Passing` here is necessary but not sufficient to call the feature
done — `ai-governance`'s Gate 3 coverage check (`SKILL.md`'s Routing &
Scope section) is the actual completion gate for the change as a whole.
