---
name: KodeLikeKevin
description: Personal coding conventions and SOLID/YAGNI workflow spanning full-stack .NET (C#/Blazor), Node.js/TypeScript/React/JavaScript/HTML, and Python. Use whenever creating, editing, reviewing, or scaffolding C#, Blazor (.razor), .csproj, TypeScript/JavaScript (.ts/.tsx/.js/.jsx), React components, HTML, package.json-based Node projects, or Python (.py, pyproject.toml) code — including class libraries, UI components, data access layers, APIs, and unit tests.
---

# Full-Stack Coding Conventions (.NET, Node/TS/React, Python)

Apply these to all .NET, Node.js/TypeScript/React/JavaScript/HTML, and Python work
unless a project's own conventions (its CLAUDE.md or a project-scoped skill) say
otherwise. Project-level conventions always win.

## Use this skill when
- Writing or editing C#, Blazor, `.razor`, or `.csproj` files.
- Writing or editing TypeScript, JavaScript, React (`.tsx`/`.jsx`), or HTML files,
  or working in a Node.js (`package.json`-based) project.
- Writing or editing Python (`.py`, `pyproject.toml`) files.
- Scaffolding new projects, components, or libraries in any of the above.
- Reviewing code in any of the above for convention compliance.

## Reach for another skill when
- The task involves none of the languages/ecosystems above.
- A project-scoped skill or CLAUDE.md defines conflicting conventions — defer to those.
- For C#/.NET specifics, this skill defers to the specialized installed skills
  (csharp-async, efcore-mssql, dotnet-testing, aspnet-minimal-api-openapi,
  csharp-docs, dotnet-best-practices) — see "Additional practices" below. No
  equivalent specialized skills are currently installed for TypeScript/Node/React
  or Python, so this skill owns those conventions directly via its reference
  files; if such skills are added later, defer to them the same way.

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

## Naming

### C# / .NET
- **PascalCase** — types, methods, properties, events, public fields, namespaces.
- **camelCase** — local variables and method parameters.
- **_camelCase** (leading underscore) — private instance fields.
- Interfaces prefixed with `I` (e.g. `IUserRepository`).
- Async methods suffixed with `Async`.

### TypeScript / JavaScript / React / HTML
- **camelCase** — variables, functions, method names.
- **PascalCase** — React components, classes, TypeScript types/interfaces.
- **UPPER_SNAKE_CASE** — module-level constants.
- **kebab-case** — filenames, except a component file matches its exported
  component's PascalCase name (e.g. `UserCard.tsx`). CSS classes: kebab-case.

### Python
- **snake_case** — functions, variables, modules, packages.
- **PascalCase** — classes.
- **UPPER_SNAKE_CASE** — module-level constants.
- **_leading_underscore** — internal/non-public names (PEP 8); reserve dunder
  names (`__init__`, etc.) for actual special methods.

## Blazor components (.NET)
- Default to code-behind: `Dashboard.razor` pairs with `Dashboard.razor.cs`.
- Add `Dashboard.razor.css` (scoped CSS) **only** when the component has its own styling.
- Add `Dashboard.razor.js` (collocated JS module) **only** when the component needs JS interop.
- Do not create empty `.js`/`.css` files for components that don't need them.

## React components
- Function components with hooks only — no class components.
- One component per file, filename matching the component's PascalCase name.
- Type props with a TypeScript `interface`, not `PropTypes`.
- Keep components presentational where practical; push logic into hooks or
  services (single responsibility).
- Don't reach for `useEffect` where derived state or an event handler would do.
- Don't add `useMemo`/`useCallback` speculatively — only once a real performance
  need is demonstrated (YAGNI).

## Data access
- Use the Repository pattern for the data-access layer, regardless of language
  (e.g. a .NET DAL project, a Node data-access module, a Python repository
  class) — keep it isolated from business logic.
- Repositories expose intent-revealing methods rather than leaking the
  underlying query builder/ORM type (e.g. `IQueryable`, a Prisma/SQLAlchemy
  query object), unless a specific need justifies otherwise.

## Testing
- Every component and every piece of backend functionality has corresponding unit tests.
- Use the idiomatic framework for the language: NUnit (C#), **Vitest + React
  Testing Library** (TypeScript/JavaScript/React), pytest (Python). If no test
  project/setup exists yet, create one and backfill tests for anything
  currently untested.
- Cover edge cases. Include both passing (happy-path) and failing (guard/error) cases.

## Documentation requirements
- **APIs**: any time you add or change a public API surface (endpoint,
  controller action, public function/method/class other code depends on),
  add or update the language's doc-comment convention and keep OpenAPI/
  Swagger annotations current. See `references/documentation.md`.
- **Web applications**: any time you add or change a user-facing page/feature
  (Blazor or React), add or update its markdown doc under `docs/user/`. See
  `references/documentation.md`.

## Code provenance & licensing
When code is adapted from an identifiable external source (a doc page,
Stack Overflow answer, OSS repo, blog post, etc.) rather than written from
general knowledge, add a short attribution comment above it citing the
source URL and license (if stated/known). See `references/code-attribution.md`
for format.

## Additional practices

### C# / .NET
For async, EF Core, testing frameworks, minimal API/OpenAPI, and XML doc
conventions, defer to the specialized skills already installed
(csharp-async, efcore-mssql, dotnet-testing, aspnet-minimal-api-openapi,
csharp-docs, dotnet-best-practices) rather than restating them here. For
nullable reference types, DI/configuration, logging/error handling, and
project layout conventions specific to this skill, see
`references/csharp-dotnet-practices.md`.

### TypeScript / Node / React / JavaScript / HTML
No specialized skill is currently installed for this ecosystem, so this
skill owns these conventions directly. See
`references/typescript-node-react-practices.md` for TypeScript strictness,
Node.js patterns, React/hooks conventions, HTML, and testing tooling.

### Python
No specialized skill is currently installed for Python, so this skill owns
these conventions directly — see `references/python-practices.md`, which
includes the Zen of Python applied literally, line by line.

## References to load on demand
- `references/documentation.md` — API dev doc and web app user doc conventions and templates.
- `references/code-attribution.md` — when and how to attribute adapted external code.
- `references/csharp-dotnet-practices.md` — nullable types, DI/config, logging, project layout.
- `references/typescript-node-react-practices.md` — TypeScript strictness, Node.js
  patterns, React/hooks conventions, HTML, and testing tooling.
- `references/python-practices.md` — PEP 8/257, typing, testing, and the Zen of
  Python applied to the letter.
