# Resolving a Clarification Gate

Loaded only when a `klk-` command actually refuses on `gate-clarifications`
(or another missing prerequisite) — not needed on a normal run. The loop
back to progress:

1. The user answers the named question(s), in chat or by editing the
   artifact directly.
2. Edit the artifact **in place**: replace the `NEEDS CLARIFICATION: <question>`
   text with the resolved requirement, at the same `REQ-*`/`CON-*`/`TS-*`/
   `AC-*` ID — don't delete the item or renumber IDs, and don't bury the
   resolution somewhere else in the document. This keeps every ID stable
   for anything that already traces to it.
3. Re-invoke the same command (which re-runs `gate-clarifications` itself),
   or run that check directly first if just confirming before re-invoking.
   Either way the gate re-reads the artifact from disk — it never assumes
   it's satisfied just because the user said so in chat.
4. If multiple markers existed, resolving some but not all still blocks —
   the command refuses again and names only the ones still open.
