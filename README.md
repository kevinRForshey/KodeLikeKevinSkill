# KodeLikeKevinSkill

This is my personal Claude Code skill for how I want *all* code written,
with an additional layer of conventions for full-stack .NET development (C#
and Blazor). It encodes conventions and safeguards drawn from 15 years of
software development, so Claude writes code the way I would — instead of
re-explaining my preferences on every project. The general principles apply
no matter what language or stack is in play; the .NET/C#/Blazor section
applies on top of those specifically for .NET work.

## Principles behind this skill

- **KISS, always.** Avoid complex code whenever possible. Complexity is
  anything about a system's structure that makes it harder to understand or
  modify — unnecessary indirection, premature abstraction, deep nesting,
  excess configurability, tangled control flow. Prefer the simplest design
  that correctly solves the problem in front of you.
- **SOLID first, patterns second.** Single responsibility comes first;
  additional abstractions (interfaces, design patterns) are introduced only
  when a concrete need exists, never speculatively (YAGNI).
- **Clarity over cleverness.** Readable, explicit code beats compact or
  clever code.
- **Simplicity by default.** Reach for extra design patterns only when SOLID
  or a real requirement calls for them.
- **Nothing ships undocumented or untested.** Public API changes get XML
  docs and current OpenAPI annotations; user-facing features get end-user
  docs; all components and backend functionality get unit tests, including
  edge cases.
- **Adapted code is attributed.** Code drawn from an identifiable external
  source (a doc page, Stack Overflow answer, OSS repo, blog post) is cited
  with its source and license; code written from general knowledge is not.
- **Git stays under my control.** Claude never runs `git commit` or
  `git push` unless I explicitly ask for that specific action in the current
  conversation — read-only git commands and staging are fine.
- **Token efficiency without cutting corners.** Claude should conserve
  context (avoid re-reading files, prefer targeted edits/greps, batch
  read-only work) but never use that as an excuse to skip a required
  deliverable like tests or docs.
- **Project conventions win.** A project's own CLAUDE.md or project-scoped
  skill always overrides the conventions here.
- **Direct, not agreeable.** State real problems and tradeoffs plainly; skip
  unearned praise; push back on scope creep and over-engineering.
- **Plan before changing code, validate before calling it done.** Non-trivial
  changes get a short plan and a go-ahead first; finished work gets checked
  against the actual requirement and edge cases, not just "does it compile."

## Spec-driven development commands

Six `klk-`prefixed commands carry a feature from a plain-language
description to tested, implemented code: `klk-create-spec` →
`klk-create-tech-spec` → `klk-create-tests` → `klk-create-stories` →
`klk-implement-stories` → `klk-run-qa`. The load-bearing design choice:
tests are written from the technical spec, *before* stories exist — the
Definition of Done (`tests.md`) is fixed before any task breakdown happens,
so later story-writing can't quietly redefine what "done" means. Stories
cite which already-written tests they're responsible for turning green
rather than inventing their own acceptance criteria.

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
in both a backend (Python) and frontend (TypeScript/React) stack. It
hasn't yet been run through a .NET/C# worked example specifically.

## What each file does

- **`SKILL.md`** — The skill's entry point, kept deliberately lean since it
  loads in full every time the skill triggers. It holds only what's
  universal across .NET, Node/TS/React, and Python: KISS/SOLID/YAGNI,
  clarity-over-cleverness, version-control and token-efficiency guardrails,
  the Repository-pattern rule for data access, the testing bar, and
  pointers to the reference files below plus the specialized skills to
  defer to for C#/.NET specifics (e.g. `csharp-async`, `efcore-mssql`,
  `dotnet-testing`). This is the file Claude reads first and treats as the
  source of truth; everything language-specific lives one hop away so a
  single-language task doesn't pay to load conventions for the other two.

- **`references/csharp-dotnet-practices.md`** — Loaded on demand for C#/
  .NET/Blazor work: naming conventions, Blazor code-behind/scoped-file
  rules, nullable reference types, use of `record` types and pattern
  matching, DI service lifetimes and the options pattern for configuration,
  structured logging and exception-handling boundaries, and layered
  solution/project structure.

- **`references/typescript-node-react-practices.md`** — Loaded on demand
  for TypeScript/JavaScript/React/Node/HTML work: naming conventions,
  TypeScript strictness, React/hooks component conventions, a Next.js App
  Router subsection, Node.js patterns, HTML semantics/accessibility, and
  testing tooling (Vitest + React Testing Library).

- **`references/python-practices.md`** — Loaded on demand for Python work:
  naming conventions, PEP 8 style and dependency management, typing
  (including Pydantic for FastAPI schemas), PEP 257 docstrings, pytest
  conventions, EEG/EDF-style signal-processing notes, and the Zen of Python
  applied literally.

- **`references/documentation.md`** — Loaded on demand when API or
  user-facing changes are made. Details exactly what's required for API
  developer documentation (doc comments + OpenAPI/Swagger annotations,
  per language) and for end-user documentation of Blazor/React features
  (`docs/user/*.md`), including when a new doc file is warranted versus
  updating an existing one.

- **`references/code-attribution.md`** — Loaded on demand when code is
  adapted from an external source. Defines what counts as an "identifiable
  source" requiring attribution, the comment format to use
  (`// Source: <url> (<license>) — <note>`), and how to handle sources with
  an unstated license.

- **`references/sdd-overview.md`** — Loaded once per SDD command
  invocation. The shared artifact layout (`docs/sdd/<feature-slug>/`:
  `spec.md` → `tech-spec.md` → `tests.md` → `stories.md`), the story status
  model (`Ready for Implementation` → `Implemented` → `Passing`),
  and the gate/traceability rules all six `klk-` commands follow.

- **`references/sdd-create-spec.md`**, **`sdd-create-tech-spec.md`**,
  **`sdd-create-tests.md`**, **`sdd-create-stories.md`**,
  **`sdd-implement-stories.md`**, **`sdd-run-qa.md`** — One file per `klk-`
  command, loaded on demand for the command actually invoked: a plain
  description into `spec.md`; `spec.md` into `tech-spec.md` (the technical
  design plus acceptance criteria); `tech-spec.md`'s acceptance criteria
  into failing tests and `tests.md` (the Definition of Done); `tests.md`
  into an implementation-sized `stories.md` breakdown; stories into passing
  code; and a real test run into each story's final status.

- **`scripts/sdd_check.py`** — The deterministic gate logic every `klk-`
  command runs against, rather than eyeballing markdown: slug derivation,
  `NEEDS CLARIFICATION` detection (shared by `spec.md`/`tech-spec.md`),
  REQ-to-TS/AC coverage, AC-to-test coverage, story status/AC validation,
  and status edits that refuse any transition that isn't a legal single
  step in the story status machine. `scripts/tests/test_sdd_check.py` is
  its own unit-test suite (`python3 -m unittest discover -s scripts/tests`)
  — the thing enforcing this skill's testing discipline is itself held to
  it, including CLI-level tests that invoke the script as a real
  subprocess, not just its functions.

- **`scripts/sdd_gate_hook.py`** — Optional `PreToolUse` hook that makes
  the four mechanical gates above unconditional rather than dependent on
  the model choosing to run them: wired into a project's own
  `.claude/settings.json`, it blocks a `Write`/`Edit` of
  `tech-spec.md`/`tests.md`/`stories.md` outright when that file's
  prerequisite gate isn't met. See `references/sdd-overview.md`'s
  "Optional: making the four mechanical gates unconditional" section for
  the exact settings.json snippet. Its own tests
  (`scripts/tests/test_sdd_gate_hook.py`) invoke it the same way Claude
  Code does — JSON piped to stdin — not just its functions directly.

- **`.github/workflows/test.yml`** — Runs that same unit-test suite on every
  push/PR, against Python 3.9 and 3.12, so a regression in the gate script
  can't land silently.

- **`LICENSE`** — Apache License 2.0 covering this skill's contents.

- **`.gitignore`** — Excludes OS/editor cruft, the disposable
  `.superpowers/sdd/` scratch workspace created when a plan is executed with
  the `subagent-driven-development` skill in this repo, and the `docs/sdd/`
  worked examples plus their real backing code under `examples/` (both kept
  on disk for validation, untracked so they don't bloat history).
