# SDD Commands — Shared Conventions

Cross-cutting rules every `klk-` SDD command follows. Read this once per SDD
command invocation, before loading that command's own reference file.

## Pipeline and artifact layout
Six commands carry a feature from a plain-language description to verified
code, each writing one artifact the next reads:

| # | Command | Reads | Writes |
|---|---|---|---|
| 1 | `klk-create-spec` | a feature description | `spec.md` |
| 2 | `klk-create-tech-spec` | approved `spec.md` | `tech-spec.md` |
| 3 | `klk-create-tests` | approved `tech-spec.md` | failing tests + `tests.md` |
| 4 | `klk-create-stories` | `tests.md` (+ `spec.md`/`tech-spec.md`) | `stories.md` |
| 5 | `klk-implement-stories` | `stories.md` | production code |
| 6 | `klk-run-qa` | implemented stories | test-run report |

The load-bearing design point: **tests are written from the technical spec,
before stories exist.** `tests.md` is what makes the tests real and
traceable — it's the Definition of Done for the feature. Stories, created
afterward, don't invent new acceptance criteria; each one cites which
already-existing AC/tests it's responsible for turning green. This keeps
"what does done mean" fixed before any implementation-sized task breakdown
happens, instead of letting task breakdown quietly redefine done.

All artifacts live under `docs/sdd/<feature-slug>/`, where `<feature-slug>`
is a kebab-case slug derived from the feature description (e.g.
`user-password-reset`). Derive it with
`python3 scripts/sdd_check.py slug "<description>"` rather than guessing by
eye, so the same feature lands in the same directory across commands run in
separate turns. Reuse the same slug/directory across all six commands for
one feature — never create a second directory for the same feature.

- `spec.md` — written by `klk-create-spec`. **What**: functional
  requirements (`REQ-*`), constraints (`CON-*`), success criteria (`SC-*`).
- `tech-spec.md` — written by `klk-create-tech-spec`. **How**: technical
  design items (`TS-*`) mapped to `REQ-*`, and the Given/When/Then
  acceptance criteria (`AC-*`) that tests will be written against.
- `tests.md` — written by `klk-create-tests`. A manifest, not the tests
  themselves: for each `AC-*`, the real test name(s)/file path(s) that
  verify it, confirmed red at the time this file was written. This is the
  feature's Definition of Done.
- `stories.md` — written by `klk-create-stories`, then updated in place by
  `klk-implement-stories` and `klk-run-qa` (status field only — never
  rewrite a story's requirements text in a later phase).

Tests and production code are **not** mirrored under `docs/sdd/`
(`tests.md` is a manifest pointing at them, not a copy) — the real files go
in the project's idiomatic test/source locations (see this skill's own
`## Testing` section and the relevant `references/*-practices.md` file for
the language in play). `docs/sdd/` holds only the planning/traceability
artifacts.

## Story status model
Each story in `stories.md` carries one status, advanced only by the command
named, one legal step at a time:
`Ready for Implementation` → `Implemented` → `Passing`
(or `Failing: <reason>`, reachable only from `Implemented`/`Passing`, and
recoverable only back to `Implemented` or `Passing` once fixed).

There's no `Draft` or "Tests Written" status in this model — tests already
exist by the time a story is created (`klk-create-stories` writes every
story straight to `Ready for Implementation`, since there's no earlier
phase for a story to be a draft of or to advance from), so no command owns
a transition into or out of either state.

Change the status field with
`python3 scripts/sdd_check.py set-status <stories.md> <US-ID> <NewStatus>`
— it rewrites only that one line, **and refuses any transition that isn't a
legal single step** (e.g. `Ready for Implementation` straight to `Passing`,
or `Passing` straight back to `Ready for Implementation`). This is what
makes "never jump a story ahead of a phase it didn't actually perform"
mechanically true instead of just a request: the script itself enforces
the state machine, not only a by-eye read of what status a story currently
claims.

## Gates — never guess past a missing prerequisite
Every command starts by checking its required input is actually ready.
Four of these checks are mechanical — run the script and treat its exit
code as the actual gate, not a read-it-and-judge-for-yourself step:
- `python3 scripts/sdd_check.py gate-clarifications <spec.md|tech-spec.md>`
  — exits 1 and lists any unresolved `NEEDS CLARIFICATION` markers. Run
  before `klk-create-tech-spec` (against `spec.md`) and before
  `klk-create-tests` (against `tech-spec.md`).
- `python3 scripts/sdd_check.py gate-coverage <spec.md> <tech-spec.md>` —
  exits 1 if any `REQ-*` defined in `spec.md` isn't cited by at least one
  `TS-*` and at least one `AC-*` in `tech-spec.md`'s bracket annotations.
  Run at the end of `klk-create-tech-spec`, alongside its own
  `gate-clarifications` check — this is what makes rule 3 in that
  command's own reference file (every `REQ-*` covered) an actual gate
  instead of a self-check the model can forget to run.
- `python3 scripts/sdd_check.py gate-tests <tests.md> --acs <AC-IDs>` —
  exits 1 if `tests.md` is missing, or if any named `AC-*` has zero
  recorded test entries. Run before `klk-create-stories` for the AC(s) the
  upcoming stories will cite.
- `python3 scripts/sdd_check.py gate-stories <stories.md> --ids <US-IDs> --status <allowed statuses>`
  — exits 1 if any targeted story isn't at an allowed status or has zero
  acceptance criteria. Run before `klk-implement-stories` and `klk-run-qa`
  to confirm the stories about to be touched are actually ready for that
  phase.

The remaining gates require judgment a script can't supply, and stay
manual:
- Tests in `tests.md` claimed red with no actual failing run observed.
- A story claimed `Implemented` with no passing test run backing it.

When a gate isn't met (script exit 1, or a manual check fails), name exactly
what's missing and stop — don't produce a document or code that looks
complete to paper over the gap.

### Optional: making the four mechanical gates unconditional
The four `gate-*` commands above are only as real as the discipline of
actually running them — nothing stops a model from writing `tech-spec.md`
without first running `gate-clarifications` against `spec.md`. Projects
that want the gate enforced regardless of whether it was invoked can wire
`scripts/sdd_gate_hook.py` in as a `PreToolUse` hook in that project's
`.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PROJECT_DIR}/scripts/sdd_gate_hook.py\""
          }
        ]
      }
    ]
  }
}
```

The hook reads the same `spec.md`/`tech-spec.md`/`tests.md` the `gate-*`
commands read, and blocks (exit 2) a `Write`/`Edit` of
`tech-spec.md`/`tests.md`/`stories.md` outright when that file's
prerequisite gate isn't met — no agent compliance required. It's a no-op
for every other file path, so enabling it doesn't affect unrelated work.
This is opt-in rather than shipped on by default: it only applies within a
project that adds it to its own `.claude/settings.json`, consistent with
project conventions always winning over this skill's own defaults.

## Resolving a clarification gate and continuing
When a command refuses because of a `NEEDS CLARIFICATION` marker (or any
other missing prerequisite), the loop back to progress is:

1. The user answers the named question(s), in chat or by editing the
   artifact directly.
2. Edit the artifact **in place**: replace the `NEEDS CLARIFICATION: <question>`
   text with the resolved requirement, at the same `REQ-*`/`CON-*`/`TS-*`/
   `AC-*` ID — don't delete the item or renumber IDs, and don't bury the
   resolution somewhere else in the document. This keeps every ID stable
   for anything that already traces to it.
3. Re-invoke the same command (which re-runs `gate-clarifications` itself),
   or run that check directly first if just confirming before re-invoking.
   Either way the gate re-reads the artifact from disk — it never assumes
   it's satisfied just because the user said so in chat.
4. If multiple markers existed, resolving some but not all still blocks —
   the command refuses again and names only the ones still open.

## Traceability
Carry IDs forward through every downstream artifact: a `REQ-*` traces to
the `TS-*`/`AC-*` in `tech-spec.md` that implement it, each `AC-*` traces to
its test entry/entries in `tests.md`, and each story in `stories.md` cites
the `REQ-*`/`TS-*`/`AC-*` (and therefore the test names) it's responsible
for turning green. A commit/PR description for implementation work should
name the story IDs it closes. This is what makes `klk-run-qa`'s report
meaningful — a failing test must be traceable back to one `AC-*` and one
story, not a vague "something broke."
