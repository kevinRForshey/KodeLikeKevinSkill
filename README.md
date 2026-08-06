# KodeLikeKevinSkill

This is my personal Claude Code skill for full-stack .NET development (C# and
Blazor). It encodes conventions and safeguards drawn from 15 years of
software development, so Claude writes .NET code the way I would — instead
of re-explaining my preferences on every project.

## Principles behind this skill

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

## What each file does

- **`skill.md`** — The skill's entry point. Defines when the skill applies
  (any C#/Blazor/.NET work), the version-control and token-efficiency
  guardrails, core design principles, naming conventions, Blazor
  code-behind/scoped-file rules, data-access (Repository pattern) rules,
  testing requirements, and pointers to the other specialized/reference
  skills to defer to (e.g. `csharp-async`, `efcore-mssql`, `dotnet-testing`).
  This is the file Claude reads first and treats as the source of truth.

- **`references/documentation.md`** — Loaded on demand when API or
  user-facing changes are made. Details exactly what's required for API
  developer documentation (XML doc comments + OpenAPI/Swagger annotations)
  and for end-user documentation of Blazor features (`docs/user/*.md`),
  including when a new doc file is warranted versus updating an existing
  one.

- **`references/code-attribution.md`** — Loaded on demand when code is
  adapted from an external source. Defines what counts as an "identifiable
  source" requiring attribution, the comment format to use
  (`// Source: <url> (<license>) — <note>`), and how to handle sources with
  an unstated license.

- **`references/csharp-dotnet-practices.md`** — Loaded on demand for topics
  not owned by another installed skill: nullable reference types, use of
  `record` types and pattern matching, DI service lifetimes and the options
  pattern for configuration, structured logging and exception-handling
  boundaries, and layered solution/project structure.

- **`LICENSE`** — Apache License 2.0 covering this skill's contents.

- **`.gitignore`** — Excludes OS/editor cruft and the disposable
  `.superpowers/sdd/` scratch workspace created when a plan is executed with
  the `subagent-driven-development` skill in this repo.
