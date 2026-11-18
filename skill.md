---
name: KodeLikeKevin
description: Personal coding conventions and SOLID/YAGNI workflow spanning full-stack .NET (C#/Blazor), Node.js/TypeScript/React/JavaScript/HTML, and Python. Use whenever creating, editing, reviewing, or scaffolding C#, Blazor (.razor), .csproj, TypeScript/JavaScript (.ts/.tsx/.js/.jsx), React components, HTML, package.json-based Node projects, or Python (.py, pyproject.toml) code — including class libraries, UI components, data access layers, APIs, and unit tests.
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
  speculatively (YAGNI).
- Clarity and explicitness over cleverness.
- Reach for an additional design pattern only when SOLID, a real requirement,
  or a proven pain point calls for it — not by default.

## Data access
Use the Repository pattern for the data-access layer regardless of language,
kept isolated from business logic. Expose intent-revealing methods rather
than leaking the underlying query builder/ORM type (`IQueryable`, a
Prisma/SQLAlchemy query object), unless a specific need justifies otherwise.

## Testing
Every component and backend functionality unit has corresponding tests,
covering both happy-path and failing/guard cases, using the idiomatic
framework for the language in play: NUnit (C#), Vitest + React Testing
Library (TypeScript/JavaScript/React), pytest (Python). If no test
project/setup exists yet, create one and backfill tests for anything
currently untested.

## Documentation & attribution
- **Public API changes** (an endpoint, controller action, or public
  function/method/class other code depends on): add or update the
  language's doc-comment convention and keep OpenAPI/Swagger annotations
  current, in the same change that adds or modifies the API. See
  `references/documentation.md`.
- **User-facing page/feature changes** (Blazor or React): add or update its
  markdown doc under `docs/user/`. See `references/documentation.md`.
- **Adapted external code** (from an identifiable doc page, Stack Overflow
  answer, OSS repo, or blog post — not general knowledge): add a short
  attribution comment above it citing the source URL and license, if known.
  See `references/code-attribution.md`.

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
