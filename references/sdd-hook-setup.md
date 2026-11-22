# Making the five mechanical gates unconditional

See `sdd-overview.md` for what the five `gate-*` checks are. This file is
project setup, not something a `klk-` command needs mid-run — load it only
when actually wiring the hook into a project.

The gates are only as real as the discipline of actually running them —
nothing stops a model from writing `tech-spec.md` without first running
`gate-clarifications` against `spec.md`. Projects that want the gate
enforced regardless of whether it was invoked can wire
`scripts/sdd_gate_hook.py` in as a `PreToolUse` hook in that project's
`.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PROJECT_DIR}/scripts/sdd_gate_hook.py\""
          }
        ]
      }
    ]
  }
}
```

The hook reads the same `spec.md`/`tech-spec.md`/`tests.md`/`stories.md`
the `gate-*` commands read, and blocks (exit 2) a `Write`/`Edit` of
`tech-spec.md`/`tests.md`/`stories.md`/`pr-description.md` outright when
that file's prerequisite gate isn't met — no agent compliance required.
It's a no-op for every other file path, so enabling it doesn't affect
unrelated work.

This is opt-in rather than shipped on by default: it only applies within a
project that adds it to its own `.claude/settings.json`, consistent with
project conventions always winning over this skill's own defaults.
