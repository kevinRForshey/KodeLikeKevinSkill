# TypeScript / Node.js / React / JavaScript / HTML Practices

Detail for the "References" pointer in `skill.md`. No specialized skill is
currently installed for this ecosystem, so this skill owns these conventions
directly.

## Naming
- **camelCase** — variables, functions, method names.
- **PascalCase** — React components, classes, TypeScript types/interfaces.
- **UPPER_SNAKE_CASE** — module-level constants.
- **kebab-case** — filenames, except a component file matches its exported
  component's PascalCase name (e.g. `UserCard.tsx`). CSS classes: kebab-case.

## TypeScript strictness
- Enable `strict: true` in `tsconfig.json` — don't disable individual strict
  flags to silence errors.
- Avoid `any`; use `unknown` plus a type guard/narrowing when the type is
  genuinely unknown at that point.
- Prefer `interface` for object shapes that might be extended/implemented;
  `type` for unions, intersections, and utility-type compositions.
- Avoid non-null assertions (`!`) except where a prior check genuinely
  guarantees non-null and the compiler can't infer it.

## React components
- Function components with hooks only — no class components.
- One component per file, filename matching the component's PascalCase name.
- Type props with a TypeScript `interface`, not `PropTypes`.
- Keep components presentational where practical; push logic into hooks or
  services (single responsibility).
- Don't reach for `useEffect` where derived state or an event handler would do.
- Don't add `useMemo`/`useCallback` speculatively — only once a real
  performance need is demonstrated (YAGNI).

## Next.js (App Router)
- Default to server components; mark `"use client"` only where interactivity
  or a browser API actually requires it — don't reach for it by habit.
- Fetch data in the component/route that needs it rather than prop-drilling
  it down through many layers — a server component can fetch close to
  where it's used.
- Keep client-side state minimal; don't reach for a global store when local
  state or URL state is sufficient.

## Node.js patterns
- Use `async`/`await` over raw Promise chains or callbacks.
- Validate external input (request bodies, env vars, query params) at the
  boundary (e.g. zod, a validation middleware) rather than trusting it
  downstream.
- Load configuration/secrets from environment variables (or a secrets
  manager), never hardcoded — follow the project's existing config loader if
  one exists.

## HTML
- Use semantic elements (`<button>`, `<nav>`, `<main>`, etc.) over generic
  `<div>`/`<span>` with ARIA roles bolted on, except where no semantic
  element fits.
- Every interactive element must be keyboard-operable and have an accessible
  name (visible text, `aria-label`, or an associated `<label>`).

## Testing
- **Vitest + React Testing Library.** Test behavior (what the user/consumer
  sees or calls), not implementation details (internal state, private
  methods).
- Mock network/IO boundaries; don't mock the module under test.
- If no test setup exists yet, create one and backfill tests for anything
  currently untested.
