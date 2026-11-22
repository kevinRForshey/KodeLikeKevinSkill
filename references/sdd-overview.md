# SDD Commands — Shared Conventions

Cross-cutting rules every `klk-` SDD command follows. Read this once per SDD
command invocation, before loading that command's own reference file. For
which command reads/writes which artifact, see `SKILL.md`'s command table —
not repeated here.

## Artifact layout
All artifacts live under `docs/sdd/<feature-slug>/`. Derive the slug with
`python3 scripts/sdd_check.py slug "<description>"` rather than guessing by
eye, and reuse the same slug/directory across all seven commands for one
feature — never create a second directory for the same feature.

| Artifact | Written by | Holds |
|---|---|---|
| `spec.md` | `klk-create-spec` | `REQ-*`/`CON-*`/`SC-*` — the **what** |
| `tech-spec.md` | `klk-create-tech-spec` | `TS-*` + Given/When/Then `AC-*` — the **how** |
| `tests.md` | `klk-create-tests` | per-`AC-*` real test name(s)/path(s), confirmed red — the Definition of Done |
| `stories.md` | `klk-create-stories`; status field updated in place by `klk-implement-stories`/`klk-run-qa` | per-story requirements + status |
| `pr-description.md` | `klk-ship` | summary, closed `REQ-*`/`US-*` IDs, test plan |

A later phase updates only the status field in `stories.md` — never a
story's requirements text. Tests and production code are never mirrored
under `docs/sdd/` (`tests.md` is a manifest pointing at them, not a copy) —
they live in the project's idiomatic locations; `docs/sdd/` holds only
planning/traceability artifacts.

## Story status model
One status per story, advanced one legal step at a time by the command
named:
`Ready for Implementation` → `Implemented` → `Passing`
(or `Failing: <reason>`, reachable and recoverable only via `Implemented`/
`Passing`).

Change it with
`python3 scripts/sdd_check.py set-status <stories.md> <US-ID> <NewStatus>`
— rewrites only that line and refuses any transition that isn't a legal
single step (e.g. `Ready for Implementation` straight to `Passing`), which
is what makes "never jump a story ahead of a phase it didn't perform"
mechanically true.

## Gates — never guess past a missing prerequisite
Every command checks its required input is actually ready before
proceeding. Each command's own reference file names the exact invocation
and what to do on failure; this is just the map of which gate runs where:

| Gate | Run before | Exits 1 when |
|---|---|---|
| `gate-clarifications <spec\|tech-spec.md>` | `klk-create-tech-spec`, `klk-create-tests` | unresolved `NEEDS CLARIFICATION` markers |
| `gate-coverage <spec.md> <tech-spec.md>` | end of `klk-create-tech-spec` | a `REQ-*` missing a `TS-*`/`AC-*` |
| `gate-tests <tests.md> --acs <AC-IDs>` | `klk-create-stories` | a named `AC-*` has no test entry |
| `gate-stories <stories.md> --ids <US-IDs> --status <...>` | `klk-implement-stories`, `klk-run-qa` | a targeted story isn't at an allowed status, or has no AC |
| `gate-ship <tech-spec.md> <stories.md> [--ids <US-IDs>]` | `klk-ship` | a targeted story isn't `Passing` (or, whole-feature, an `AC-*` has no `Passing` story) |

All five are mechanical — treat the exit code as the actual gate, not a
read-it-and-judge-for-yourself step. Two checks stay manual (no script can
verify them): tests in `tests.md` claimed red with no actual failing run
observed, and a story claimed `Implemented` with no passing test run
backing it.

Either way — script exit 1, or a manual check fails — name exactly what's
missing and stop; don't produce a document or code that looks complete to
paper over the gap. If the failure is `NEEDS CLARIFICATION`, see
`references/sdd-clarification-loop.md` for how to resolve it and continue.

To make these five gates unconditional instead of relying on the model to
run them, see `references/sdd-hook-setup.md` (project setup, loaded only
when actually wiring that in).

## Traceability
Carry IDs forward through every downstream artifact: a `REQ-*` traces to
the `TS-*`/`AC-*` that implement it, each `AC-*` traces to its test
entry/entries, and each story cites the `REQ-*`/`TS-*`/`AC-*` (and
therefore test names) it's responsible for turning green. A commit/PR
description should name the story IDs it closes. This is what makes a
failing test traceable back to one `AC-*` and one story, not a vague
"something broke."
