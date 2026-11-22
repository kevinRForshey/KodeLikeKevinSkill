# Staging copy — universal `kodelikekevin` skill

This directory is **not** part of the installed `kode-like-kevin-dotnet` skill in this repo.
It's a staged replacement for the separate, synced `kodelikekevin` skill that lives at
`~/.claude/skills/synced/.../kodelikekevin/SKILL.md`.

That path is a sync cache (sits next to Anthropic's built-in skills, stamped by a
`manifest.json`/`.last-complete-round` sync process) — editing it directly gets silently
reverted on the next sync round. The real source of truth is wherever that skill was
authored (claude.ai → Skills, or the `skill-creator` skill).

## What changed vs. the current synced skill

- Cut from ~3,150 to ~650 tokens: dropped the duplicated frontmatter block, the "honesty
  note," and the closing checklist (all restated content with no new information).
- Dropped the inline .NET/C#/Blazor section entirely — that content now lives exclusively
  in this repo's `kode-like-kevin-dotnet` skill, so a .NET task no longer loads it twice.
- Moved the Python and TypeScript/Node/React sections out to `references/*.md`, loaded only
  when that language is actually in play, instead of inline in every trigger.

## To apply

Upload/paste `SKILL.md` and the two files under `references/` to replace the existing
`kodelikekevin` skill wherever it's authored, then let it re-sync to this machine.
