---
name: KodeLikeKevinSkill
description: Personal coding conventions and SOLID/YAGNI workflow spanning full-stack .NET (C#/Blazor), Node.js/TypeScript/React/JavaScript/HTML, and Python. Use whenever creating, editing, reviewing, or scaffolding C#, Blazor (.razor), .csproj, TypeScript/JavaScript (.ts/.tsx/.js/.jsx), React components, HTML, package.json-based Node projects, or Python (.py, pyproject.toml) code — including class libraries, UI components, data access layers, APIs, and unit tests. Also use whenever the user invokes a klk-prefixed spec-driven-development command (klk-create-spec, klk-create-stories, klk-create-qa, klk-implement-stories, klk-run-qa), or asks to run the full SDD pipeline for a feature.
---

# Full-Stack Coding Conventions (.NET, Node/TS/React, Python)

Apply to all .NET, Node.js/TypeScript/React/JavaScript/HTML, and Python work
unless a project's own conventions (its CLAUDE.md or a project-scoped skill)
say otherwise — project-level conventions always win.

## Use this skill when
- Writing or editing C#, Blazor, `.razor`, or `.csproj` files.
- Writing or editing TypeScript, JavaScript, React (`.tsx`/`.jsx`), or HTML
  files, or working in a Node.js (`package.json`-based) project.
- Writing or editing Python (`.py`, `pyproject.toml`) files.
- Scaffolding or reviewing code in any of the above.
- Running a `klk-`prefixed SDD command, or taking a feature from a plain
  description through spec, stories, tests, and implementation.

## Reach for another skill when
- None of the languages/ecosystems above are involved.
- A project-scoped skill or CLAUDE.md defines conflicting conventions — defer
  to those.
- For C#/.NET specifics (async, EF Core, testing frameworks, minimal
  API/OpenAPI, XML docs), defer to the installed specialized skills
  (csharp-async, efcore-mssql, dotnet-testing, aspnet-minimal-api-openapi,
  csharp-docs, dotnet-best-practices) rather than this one. No equivalent
  specialized skills are installed yet for TypeScript/Node/React or Python,
  so this skill owns those conventions directly.
- For .NET/C#, React, Python, or TypeScript work, *process* (analyze-before-
  edit planning, the 90% test-coverage floor, build/test/coverage
  verification, security/autonomy tiers) is owned by the installed
  `ai-governance` skill, not this one — apply both together: `ai-governance`
  for process, this skill for style/convention and the `klk-` SDD lifecycle.
- The target repo already has a `.specify`/spec-kit scaffold and an
  installed spec-kit-aware lifecycle skill (e.g. `MyndTek-Development-Skill`'s
  `mds-` commands) — defer to that instead of this skill's `klk-` commands to
  avoid two competing SDD systems in the same repo. This skill's `klk-`
  commands are the lightweight alternative for repos without that scaffold.
- The user wants a standalone specification document — schema, tool, data,
  infrastructure, process, architecture, or design — with no intent to run
  it through the `klk-` stories/tests/implementation lifecycle. Use the
  installed `create-specification` skill's `/spec/spec-*.md` format for
  that instead. Use `klk-create-spec` only when the spec is step one of
  actually running this skill's SDD lifecycle for a feature.
- The code touches PHI or other sensitive health data — defer to the
  installed `phi-secure-csharp`/`phi-security-review`/`phi-dapper-dal`/
  `phi-deidentification` skills for the actual handling rules; still flag
  PHI touching logs, error messages, or third-party calls as a real
  correctness issue per `## Working style` above, not a nice-to-have.

## Version control policy
Never run `git commit` or `git push` unless the user explicitly asks for that
specific action in this conversation. Status/diff/log, staging, and branching
don't require asking. Approval isn't retroactive — each commit/push is scoped
to what was asked, not a standing permission.

## Token efficiency
Work in a way that conserves tokens — a finite budget:
- Don't re-read a file already in context; trust prior tool output unless it
  may be stale.
- Prefer targeted edits over rewriting whole files.
- Grep/search for the specific symbol or section instead of reading an entire
  large file when only part of it is relevant.
- Batch independent read-only operations instead of issuing them one at a
  time across turns.
- Load only the reference file(s) below relevant to the language actually in
  play — never all of them for a single-language task.
- Keep explanations concise; skip speculative exploration the task doesn't
  need.
- Don't paste large tool outputs (build logs, test runs, full file dumps)
  verbatim — quote only the failing/relevant lines and summarize the rest.
- Reserve subagents/parallel exploration for genuinely broad or multi-part
  investigations; a single direct read or grep doesn't need one.
- Strip scratch/debug artifacts (temporary logging, commented-out attempts,
  dead code) before presenting a solution as done — they cost tokens on
  every future read of the file.

These rules govern *how* work gets done — they never justify skipping a
required deliverable (tests, docs, attribution) defined elsewhere here.

## Core principles
- **KISS.** Avoid complexity — unnecessary indirection, premature or
  speculative abstraction, deep nesting, excess configurability, tangled
  control flow, state scattered across more places than it needs to be.
  Between two designs that solve the problem, prefer the one a future reader
  can hold in their head fastest.
- **SOLID, single responsibility first.** Introduce abstractions (interfaces,
  extra patterns, layers) only when a concrete need exists — never
  speculatively (YAGNI): every function, class, and parameter added should be
  used by the current change, and tests cover current behavior, not
  speculative future behavior.
- Clarity and explicitness over cleverness.
- Reach for an additional design pattern only when SOLID, a real requirement,
  or a proven pain point calls for it — not by default.

## Working style
- **Be direct, not agreeable.** Give the technically correct answer, not the
  comfortable one — name a real problem (perf, security, maintainability, a
  footgun) before doing the work. Surface tradeoffs between two reasonable
  approaches and say which you'd pick. Skip unearned praise; push back on
  scope creep and over-engineering, including your own prior suggestions.
- **Plan-approval, test-coverage floors, and build/test/coverage
  verification are not owned here.** For .NET/C#, React, Python, or
  TypeScript work, the installed `ai-governance` skill owns that process —
  its Gate 0 (analyze & plan, blocking), Gate 1 (90% coverage floor), and
  Gate 3 (verify via the real coverage tool's exit code, not a subjective
  read) apply in full alongside this skill's style/convention rules. This
  skill never restates or softens those gates.

## Data access
Use the Repository pattern for the data-access layer regardless of language,
kept isolated from business logic. Expose intent-revealing methods rather
than leaking the underlying query builder/ORM type (`IQueryable`, a
Prisma/SQLAlchemy query object), unless a specific need justifies otherwise.

## Testing
Every component and backend functionality unit has corresponding tests,
covering both happy-path and failing/guard cases. Default to the idiomatic
framework for the language in play — xUnit (C#), Vitest + React Testing
Library (TypeScript/JavaScript/React), pytest (Python) — only when the repo
has no established framework yet. **If the repo already has one installed
(xUnit, MSTest, Jest, unittest, etc.), follow that instead** — never
introduce a second test framework alongside an existing one. For C#, this
is the same convention the installed `dotnet-testing`/`csharp-xunit`/
`csharp-mstest` skills own; defer to whichever already applies.

For .NET/C#, React, Python, and TypeScript specifically, this is only the
framework choice — the actual coverage floor (90%, enforced by the real
coverage tool's exit code) and the plan/implement/verify process around it
belong to `ai-governance`; apply both together. For plain Node.js/
JavaScript/HTML work, which `ai-governance` doesn't cover, the bar above is
the whole of it.

## Documentation & attribution
- **Public API changes** (an endpoint, controller action, or public
  function/method/class other code depends on): add or update the
  language's doc-comment convention and keep OpenAPI/Swagger annotations
  current, in the same change that adds or modifies the API. See
  `references/documentation.md`.
- **User-facing page/feature changes** (Blazor or React): add or update its
  markdown doc under `docs/user/`. See `references/documentation.md`.
- **Adapted external code** (from an identifiable doc page, Stack Overflow
  answer, OSS repo, or blog post — not general knowledge, regardless of how
  short the snippet is): add a short attribution comment above it, in the
  code itself (not just chat or a commit message), citing the source URL
  and license, if known. See `references/code-attribution.md`.
- **A standalone change summary is wanted and no existing doc covers the
  change**: produce it as a PDF (or a Word doc, if that fits the audience
  better) via the `pdf`/`docx` skill rather than hand-rolling one — factual
  and scoped to the actual diff, not the whole plan restated.

## Spec-driven development (SDD) commands
Five `klk-`prefixed commands take a feature from a plain-language description
through to tested, implemented code. Each reads the previous command's
output and refuses to proceed past a gate it hasn't met — never guesses past
a missing prerequisite. See `references/sdd-overview.md` first for the
shared artifact layout and status model every command below follows.

| Command | Reads | Writes | Loads |
|---|---|---|---|
| `klk-create-spec` | a feature description | `spec.md` | `references/sdd-create-spec.md` |
| `klk-create-stories` | an approved `spec.md` | `stories.md` | `references/sdd-create-stories.md` |
| `klk-create-qa` | stories with acceptance criteria | failing tests (red) | `references/sdd-create-qa.md` |
| `klk-implement-stories` | stories with tests written | production code (green) | `references/sdd-implement-stories.md` |
| `klk-run-qa` | implemented stories | test run report | `references/sdd-run-qa.md` |

**Typical path**: `klk-create-spec` → `klk-create-stories` → `klk-create-qa`
→ `klk-implement-stories` → `klk-run-qa`.

**Running it**: each command also works standalone (e.g. re-running
`klk-run-qa` after a fix, or `klk-implement-stories` on one story at a time).
To run the whole path as one pipeline, just ask for it (e.g. "run the full
SDD workflow for X") — execute the commands in order, but stop and report at
whichever command's gate fails (an unresolved `NEEDS CLARIFICATION`, a story
missing acceptance criteria, a test still red) rather than forcing through
to the next phase.

Load only the reference file for the command actually invoked, plus
`sdd-overview.md`.

## References — load only what the current task needs
- `references/csharp-dotnet-practices.md` — C#/.NET/Blazor naming,
  component conventions, nullable types, DI/config, logging, project layout.
- `references/typescript-node-react-practices.md` — TypeScript/JavaScript/
  React/Node/HTML naming, component conventions, strictness, testing tooling.
- `references/python-practices.md` — Python naming, PEP 8/257, typing,
  testing, and the Zen of Python applied to the letter.
- `references/documentation.md` — API dev-doc and web-app user-doc
  conventions and templates.
- `references/code-attribution.md` — when and how to attribute adapted
  external code.
