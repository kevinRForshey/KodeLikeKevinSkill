# Code Provenance & Licensing

Detail for the "Code provenance & licensing" rule in `skill.md`.

## When attribution is required

Add attribution when code is adapted from an **identifiable external
source** — you can point to where it came from:

- A specific documentation page (e.g., Microsoft Learn, a library's docs site).
- A specific Stack Overflow (or similar Q&A site) answer.
- A specific open-source repository or file.
- A specific blog post or article.

Attribution is **not required** for code written from general knowledge of a
language/framework/pattern, even if similar code exists elsewhere — e.g.,
implementing a standard repository pattern, a typical retry loop, or a common
LINQ query does not need a citation just because the pattern is common.

**Rule of thumb:** if you could name the specific page/answer/repo you
drew from, attribute it. If you're just applying a general pattern you know,
you don't need to.

## Format

Add a comment directly above the adapted code:

```csharp
// Source: https://learn.microsoft.com/en-us/dotnet/... (MIT License) — adapted for this project's retry policy.
```

Include:
1. `Source:` followed by the URL (or repo name + path if no URL applies).
2. The license in parentheses, if stated or known (e.g., `MIT License`,
   `Apache-2.0`, `public domain`).
3. Optionally, a short note on what was adapted/changed.

## Unknown license

If you can identify the source but not its license, say so rather than
guessing:

```csharp
// Source: https://example.com/some-snippet (license not stated) — verify before use in a commercial context.
```

Never assert a specific license unless it's actually stated at the source.
