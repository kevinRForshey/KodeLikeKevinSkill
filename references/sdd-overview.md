# SDD Commands — Shared Conventions

Cross-cutting rules every `klk-` SDD command follows. Read this once per SDD
command invocation, before loading that command's own reference file.

## Artifact layout
One feature lives under `docs/sdd/<feature-slug>/`, where `<feature-slug>`
is a kebab-case slug derived from the feature description (e.g.
`user-password-reset`). Reuse the same slug/directory across all five
commands for one feature — never create a second directory for the same
feature.

- `spec.md` — written by `klk-create-spec`.
- `stories.md` — written by `klk-create-stories`, then updated in place by
  `klk-create-qa`, `klk-implement-stories`, and `klk-run-qa` (status field
  only — never rewrite a story's requirements text in a later phase).

Tests and production code are **not** mirrored under `docs/sdd/` — they go
in the project's real, idiomatic test/source locations (see this skill's own
`## Testing` section and the relevant `references/*-practices.md` file for
the language in play). `docs/sdd/` holds only the planning artifacts.

## Story status model
Each story in `stories.md` carries one status, advanced only by the command
named:
`Draft` → `Ready for QA` → `Tests Written` → `Implemented` → `Passing`
(or `Failing: <reason>` if `klk-run-qa` finds a regression).

A command only ever advances a story to the status it owns. It never jumps a
story ahead of a phase it didn't actually perform.

## Gates — never guess past a missing prerequisite
Every command starts by checking its required input is actually ready:
- Missing/unresolved `NEEDS CLARIFICATION` markers in `spec.md`.
- A story in `stories.md` with no Given/When/Then acceptance criteria.
- A story claimed "Tests Written" with no test actually present/failing.
- A story claimed "Implemented" with no passing test run backing it.

When a gate isn't met, name exactly what's missing and stop — don't produce
a document or code that looks complete to paper over the gap.

## Resolving a clarification gate and continuing
When a command refuses because of a `NEEDS CLARIFICATION` marker (or any
other missing prerequisite), the loop back to progress is:

1. The user answers the named question(s), in chat or by editing the
   artifact directly.
2. Edit the artifact **in place**: replace the `NEEDS CLARIFICATION: <question>`
   text with the resolved requirement, at the same `REQ-*`/`CON-*` ID — don't
   delete the item or renumber IDs, and don't bury the resolution somewhere
   else in the document. This keeps every ID stable for anything that already
   traces to it.
3. Re-invoke the same command. It re-reads the artifact from disk — it never
   assumes the gate is now satisfied just because the user said so in chat;
   the updated file is what it checks.
4. If multiple markers existed, resolving some but not all still blocks —
   the command refuses again and names only the ones still open.

This is a real, exercised loop, not a hypothetical: a dry run of this exact
sequence (resolve → re-run → proceed) is how `klk-create-stories` was
validated against this skill's sample `spec.md`.

## Traceability
Carry the story ID (`US-00N`) through every downstream artifact: a test's
name or tag references the story it verifies; a commit/PR description for
implementation work should name the story IDs it closes. This is what makes
`klk-run-qa`'s report meaningful — a failing test must be traceable back to
one story, not a vague "something broke."
