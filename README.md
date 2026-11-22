# KodeLikeKevinSkill

This is my personal Claude Code skill for .NET/C#/Blazor engineering conventions and the
`klk-`prefixed spec-driven development (SDD) workflow. It encodes conventions and safeguards
drawn from 15 years of software development, so Claude writes .NET code the way I would —
instead of re-explaining my preferences on every project.

Language-agnostic judgment (plan-first, YAGNI, SOLID-without-stuffing, validate-before-done,
token efficiency, code attribution) lives in a separate, synced `kodelikekevin` skill, not in
this repo — this skill applies on top of that one specifically for .NET/C#/Blazor work, and
deliberately doesn't restate what the other one already covers.

## Principles behind this skill

- **KISS, always.** Avoid complex code whenever possible. Complexity is
  anything about a system's structure that makes it harder to understand or
  modify — unnecessary indirection, premature abstraction, deep nesting,
  excess configurability, tangled control flow. Prefer the simplest design
  that correctly solves the problem in front of you.
- **SOLID first, patterns second.** Single responsibility comes first;
  additional abstractions (interfaces, design patterns) are introduced only
  when a concrete need exists, never speculatively (YAGNI).
- **Nothing ships undocumented or untested.** Public API changes get XML
  docs and current OpenAPI annotations; user-facing Blazor features get
  end-user docs; all components and backend functionality get unit tests,
  including edge cases.
- **Git stays under my control.** Claude never runs `git commit` or
  `git push` unless I explicitly ask for that specific action in the current
  conversation — read-only git commands and staging are fine.
- **Project conventions win.** A project's own CLAUDE.md or project-scoped
  skill always overrides the conventions here.

## Spec-driven development commands

Seven `klk-`prefixed commands carry a feature from a plain-language
description to a ready-to-review PR: `klk-create-spec` →
`klk-create-tech-spec` → `klk-create-tests` → `klk-create-stories` →
`klk-implement-stories` → `klk-run-qa` → `klk-ship`. See `SKILL.md`'s
command table for each command's input/output/reference file.

The load-bearing design choice: tests are written from the technical spec,
*before* stories exist — the Definition of Done (`tests.md`) is fixed before
any task breakdown happens, so later story-writing can't quietly redefine
what "done" means. Stories cite which already-written tests they're
responsible for turning green rather than inventing their own acceptance
criteria. The pipeline stops at a staged, traceable PR draft — `klk-ship`
never commits or pushes; that stays the user's call, per this skill's
version-control policy.

Each command reads the previous one's output and refuses to advance past a
gate it hasn't actually met (an unresolved ambiguity, an AC with no test
recorded, a story with no acceptance criteria, a test that isn't really
failing or passing) — no step is allowed to paper over a gap to look done.
They can be run one at a time, or chained as one pipeline on request; a
chained run still stops at the first unmet gate rather than forcing
through. See `references/sdd-overview.md` for the shared artifact layout
this whole lifecycle uses.

The gate mechanism itself is language-agnostic by design — it parses only
the planning markdown (`spec.md`/`tech-spec.md`/`tests.md`/`stories.md`),
never source code — and has been exercised end-to-end via worked examples
in a backend (Python) stack, a frontend (TypeScript/React) stack, and a
.NET/C# stack (a Repository-pattern service with a `record`-based DTO,
nullable-aware rule lookup, and real `dotnet test` runs confirming each
test red before the implementation existed and green after). Those worked
examples predate this skill's narrowing to .NET-only; the gate scripts
still work the same way for any language, even though this skill's own
prose now assumes C#.

## What each file does

- **`SKILL.md`** — The skill's entry point, kept deliberately lean since it
  loads in full every time the skill triggers. Covers .NET/Blazor/SDD
  routing, version control, and the `klk-` command table; defers to the
  `kodelikekevin` skill for everything language-agnostic rather than
  restating it.

- **`references/csharp-dotnet-practices.md`** — Loaded on demand for C#/
  .NET/Blazor work: naming conventions, Blazor code-behind/scoped-file
  rules, nullable reference types, use of `record` types and pattern
  matching, DI service lifetimes and the options pattern for configuration,
  structured logging and exception-handling boundaries, and layered
  solution/project structure. Scoped to skip what the installed
  `dotnet-best-practices` skill already covers.

- **`references/documentation.md`** — Loaded on demand when API or
  user-facing changes are made. Details what's required for .NET API
  developer documentation (doc comments + OpenAPI/Swagger annotations)
  and for end-user documentation of Blazor features (`docs/user/*.md`),
  including when a new doc file is warranted versus updating an existing
  one.

- **`references/sdd-overview.md`** — Loaded once per SDD command
  invocation. The shared artifact layout (`docs/sdd/<feature-slug>/`:
  `spec.md` → `tech-spec.md` → `tests.md` → `stories.md` →
  `pr-description.md`), the story status model (`Ready for Implementation`
  → `Implemented` → `Passing`), and the gate/traceability rules all seven
  `klk-` commands follow.

- **`references/sdd-hook-setup.md`** — Loaded only when actually wiring the
  optional `PreToolUse` gate-enforcement hook into a project's own
  `.claude/settings.json`; not needed to run any `klk-` command itself.

- **`references/sdd-create-spec.md`**, **`sdd-create-tech-spec.md`**,
  **`sdd-create-tests.md`**, **`sdd-create-stories.md`**,
  **`sdd-implement-stories.md`**, **`sdd-run-qa.md`**, **`sdd-ship.md`** —
  One file per `klk-` command, loaded on demand for the command actually
  invoked: a plain description into `spec.md`; `spec.md` into `tech-spec.md`
  (the technical design plus acceptance criteria); `tech-spec.md`'s
  acceptance criteria into failing tests and `tests.md` (the Definition of
  Done); `tests.md` into an implementation-sized `stories.md` breakdown;
  stories into passing code; a real test run into each story's final
  status; and, once every story is `Passing`, a traceable `pr-description.md`
  draft plus a staged (never committed) diff.

- **`scripts/sdd_check.py`** — The deterministic gate logic every `klk-`
  command runs against, rather than eyeballing markdown: slug derivation,
  `NEEDS CLARIFICATION` detection (shared by `spec.md`/`tech-spec.md`),
  REQ-to-TS/AC coverage, AC-to-test coverage, AC-to-story coverage, story
  status/AC validation, and status edits that refuse any transition that
  isn't a legal single step in the story status machine.
  `scripts/tests/test_sdd_check.py` is its own unit-test suite
  (`python3 -m unittest discover -s scripts/tests`) — the thing enforcing
  this skill's testing discipline is itself held to it, including
  CLI-level tests that invoke the script as a real subprocess, not just
  its functions.

- **`scripts/sdd_gate_hook.py`** — Optional `PreToolUse` hook that makes
  the five mechanical gates above unconditional rather than dependent on
  the model choosing to run them: wired into a project's own
  `.claude/settings.json`, it blocks a `Write`/`Edit` of
  `tech-spec.md`/`tests.md`/`stories.md`/`pr-description.md` outright when
  that file's prerequisite gate isn't met. See `references/sdd-hook-setup.md`
  for the exact settings.json snippet. Its own tests
  (`scripts/tests/test_sdd_gate_hook.py`) invoke it the same way Claude
  Code does — JSON piped to stdin — not just its functions directly.

- **`scripts/token_budget.py`** — Measures the estimated token cost of
  every load path through this skill (the bare `SKILL.md` trigger, and
  `SKILL.md` + `sdd-overview.md` + each `klk-` command's own reference
  file) against a ceiling, so a future edit can't quietly re-inflate what
  gets loaded without CI catching it.

- **`.github/workflows/test.yml`** — Runs that same unit-test suite, plus
  the token budget check, on every push/PR, against Python 3.9 and 3.12,
  so a regression in the gate script or a token-budget blowout can't land
  silently.

- **`universal-skill/`** — Not part of this installed skill. A staged
  replacement for the separate `kodelikekevin` skill (see its own
  `README.md`), kept here so the two skills' division of responsibility is
  reviewable in one repo even though they're authored/synced separately.

- **`LICENSE`** — Apache License 2.0 covering this skill's contents.

- **`.gitignore`** — Excludes OS/editor cruft, the disposable
  `.superpowers/sdd/` scratch workspace created when a plan is executed with
  the `subagent-driven-development` skill in this repo, and the `docs/sdd/`
  worked examples plus their real backing code under `examples/` (both kept
  on disk for validation, untracked so they don't bloat history).
