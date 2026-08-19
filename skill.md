---
name: KodeLikeKevin
description: General coding conventions that apply to all code, plus additional conventions for full-stack .NET applications in C# and Blazor. Use whenever writing, editing, or reviewing any code — the general principles (KISS/simplicity, SOLID, token efficiency, version control, attribution) always apply. The .NET-specific sections apply on top of those whenever the work involves C#, Blazor (.razor), .csproj, or other .NET code.
---

# Kode Like Kevin — Coding Conventions

## Use this skill when
- Writing, editing, or reviewing code in **any** language — apply the
  "General principles" sections below.
- Additionally writing or editing C#, Blazor, `.razor`, or `.csproj` files,
  or scaffolding/reviewing .NET projects — apply the ".NET / C# / Blazor
  specific" section as well, on top of the general one.

## Reach for another skill when
- A project-scoped skill or CLAUDE.md defines conflicting conventions —
  defer to those. Project-level conventions always win.

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
(tests, docs, or attribution) defined elsewhere in this skill.

## Core principles
- **Keep it simple. Always follow KISS (Keep It Simple, Stupid).** Avoid
  complex code whenever possible. Complexity is anything about a software
  system's *structure* that makes it harder to understand or modify —
  unnecessary indirection, premature or speculative abstraction, deep
  nesting, excess configurability, tangled control flow, or state scattered
  across more places than it needs to be. When choosing between two designs
  that solve the problem, prefer the one a future reader can hold in their
  head fastest.
- Follow SOLID closely. Single responsibility first. Introduce abstractions
  (interfaces, extra patterns, layers) only when a concrete need exists —
  never speculatively (YAGNI). This is KISS applied to structure.
- Prefer clarity and explicitness over cleverness. Readable beats clever.
- Reach for an additional design pattern only when SOLID, a real
  requirement, or a proven pain point calls for it — not by default.

## Code provenance & licensing
When code is adapted from an identifiable external source (a doc page,
Stack Overflow answer, OSS repo, blog post, etc.) rather than written from
general knowledge, add a short attribution comment above it citing the
source URL and license (if stated/known). See `references/code-attribution.md`
for format. This applies to code in any language.

---

# .NET / C# / Blazor specific

Apply the following **in addition to** the general principles above,
whenever the work involves C#, Blazor, `.razor`, or `.csproj` files.
Project-level conventions still win over anything here.

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

## Additional C#/.NET practices
For async, EF Core, testing frameworks, minimal API/OpenAPI, and XML doc
conventions, defer to the specialized skills already installed
(csharp-async, efcore-mssql, dotnet-testing, aspnet-minimal-api-openapi,
csharp-docs, dotnet-best-practices) rather than restating them here. For
nullable reference types, DI/configuration, logging/error handling, and
project layout conventions specific to this skill, see
`references/csharp-dotnet-practices.md`.

## References to load on demand
- `references/documentation.md` — API dev doc and web app user doc conventions and templates. (.NET-specific)
- `references/code-attribution.md` — when and how to attribute adapted external code. (general)
- `references/csharp-dotnet-practices.md` — nullable types, DI/config, logging, project layout. (.NET-specific)
-  For Any Code that is licensed, always include a link to where it came from and the license. If you are unsure, indicate in the comment that you are unsure of the license. If you are adapting code from a source, include a link to the source and the license if known. If you are unsure, indicate in the comment that you are unsure of the license.
