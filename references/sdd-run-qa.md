# klk-run-qa

See `sdd-overview.md` for artifact layout and gates before using this file.
This is the independent verification gate — it runs tests, it doesn't fix
them.

**Input**: stories in `stories.md`, typically at status `Implemented`, but
this command can be run at any time as a checkpoint (e.g. to check nothing
regressed).
**Output**: a test-run report; each story's status updated to `Passing` or
`Failing: <reason>`.

1. Identify the test project(s)/suite(s) covering the targeted stories (via
   their tests' story-ID tags/names from `klk-create-qa`) and run them for
   real — never infer a pass/fail result from reading the code.
2. For each targeted story:
   - All its tests pass → update status to `Passing`.
   - Any test fails → update status to `Failing: <one-line reason from the
     actual failure output>` — don't leave it at `Implemented` silently,
     and don't guess at the cause beyond what the failure actually shows.
3. Run the full suite, not just the targeted story's tests, when checking
   for regressions after `klk-implement-stories` — a story going green
   should not take a previously-`Passing` story's tests down with it. If it
   did, report that story as `Failing: regression — <reason>` too.
4. **Don't attempt fixes here.** If failures are found, report them plainly
   with the story ID, the test name, and the actual failure message/
   assertion — fixing is `klk-implement-stories`'s job, invoked again.
5. Summarize: story IDs now `Passing`, story IDs `Failing` with reasons, and
   whether the full suite is green.

This command is what makes a story's `Passing` status trustworthy — never
set it from anything short of an actual observed green run.

For .NET/C#, React, Python, or TypeScript, all stories `Passing` here is
necessary but not sufficient to call the whole feature done — `ai-governance`'s
Gate 3 (the real coverage-tool exit code, not this command's per-story pass/
fail) is still the actual completion gate for the change as a whole.
