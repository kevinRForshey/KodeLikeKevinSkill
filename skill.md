---
name: KodeLikeKevin
description: Conventions and workflow for writing full-stack .NET applications in C# and Blazor. Use whenever creating, editing, reviewing, or scaffolding C#, Blazor (.razor), .csproj, or any other .NET code — including class libraries, Blazor Server/WebAssembly components, data access layers, and unit tests. Do not use for non-.NET work.
---

# Full-Stack .NET (C# / Blazor) Conventions

Apply these to all .NET work unless a project's own conventions (its CLAUDE.md or a
project-scoped skill) say otherwise. Project-level conventions always win.

## Use this skill when
- Writing or editing C#, Blazor, `.razor`, or `.csproj` files.
- Scaffolding new .NET projects, components, or libraries.
- Reviewing .NET code for convention compliance.

## Reach for another skill when
- The task involves no C#/Blazor/.NET code.
- A project-scoped skill or CLAUDE.md defines conflicting conventions — defer to those.

## Version control policy
Never run `git commit` or `git push` unless the user explicitly asks for that
specific action in this conversation. Staging, branching, and read-only git
commands (status/diff/log) don't require asking. Don't infer permission from
an earlier commit/push approval — each one is scoped to what was asked.

## Token efficiency
Work in a way that conserves tokens/context, since it's a finite budget:
- Don't re-read a file already in context; trust prior tool output unless it may be stale.
- Prefer targeted edits over rewriting whole files when only part of a file changes.
- Grep/search for the specific symbol or section instead of reading an entire large file
  when only part of it is relevant.
- Batch independent read-only operations instead of issuing them one at a time across turns.
- Keep explanations concise — state results and decisions, don't restate code or context
  already visible in the conversation.
- Skip speculative exploration ("let me also check X just in case") when it isn't needed to
  complete the task.

These rules govern *how* work gets done — they never justify skipping a required deliverable
(tests, XML docs, OpenAPI annotations, user docs, or attribution) defined elsewhere in this skill.

## Core principles
- Follow SOLID closely. Single responsibility first. Introduce abstractions
  (interfaces, extra patterns) only when a concrete need exists — never speculatively (YAGNI).
- Prefer clarity and explicitness over cleverness. Readable beats clever.
- Keep it simple. Use additional design patterns only when SOLID or a real
  requirement calls for them, not by default.

## Naming (standard C# conventions)
- **PascalCase** — types, methods, properties, events, public fields, namespaces.
- **camelCase** — local variables and method parameters.
- **_camelCase** (leading underscore) — private instance fields.
- Interfaces prefixed with `I` (e.g. `IUserRepository`).
- Async methods suffixed with `Async`.
- JavaScript identifiers: camelCase. CSS classes: kebab-case.

## Blazor components
- Default to code-behind: `Dashboard.razor` pairs with `Dashboard.razor.cs`.
- Add `Dashboard.razor.css` (scoped CSS) **only** when the component has its own styling.
- Add `Dashboard.razor.js` (collocated JS module) **only** when the component needs JS interop.
- Do not create empty `.js`/`.css` files for components that don't need them.

## Data access
- Use the Repository pattern; keep repositories in the data-access (DAL) project.
- Repositories expose intent-revealing methods rather than leaking `IQueryable`,
  unless a specific need justifies otherwise.

## Testing
- Every component and every piece of backend functionality has corresponding unit tests.
- Use NUnit. If no NUnit test project exists, create one and backfill tests for
  anything currently untested.
- Cover edge cases. Include both passing (happy-path) and failing (guard/error) cases.

## Documentation requirements
- **APIs**: any time you add or change a public API surface (endpoint,
  controller action, public method/class), add or update XML doc comments
  and keep OpenAPI/Swagger annotations current. See `references/documentation.md`.
- **Web applications**: any time you add or change a user-facing Blazor
  page/feature, add or update its markdown doc under `docs/user/`. See
  `references/documentation.md`.

## Code provenance & licensing
When code is adapted from an identifiable external source (a doc page,
Stack Overflow answer, OSS repo, blog post, etc.) rather than written from
general knowledge, add a short attribution comment above it citing the
source URL and license (if stated/known). See `references/code-attribution.md`
for format.

## Additional C#/.NET practices
For async, EF Core, testing frameworks, minimal API/OpenAPI, and XML doc
conventions, defer to the specialized skills already installed
(csharp-async, efcore-mssql, dotnet-testing, aspnet-minimal-api-openapi,
csharp-docs, dotnet-best-practices) rather than restating them here. For
nullable reference types, DI/configuration, logging/error handling, and
project layout conventions specific to this skill, see
`references/csharp-dotnet-practices.md`.

## References to load on demand
- `references/documentation.md` — API dev doc and web app user doc conventions and templates.
- `references/code-attribution.md` — when and how to attribute adapted external code.
- `references/csharp-dotnet-practices.md` — nullable types, DI/config, logging, project layout.