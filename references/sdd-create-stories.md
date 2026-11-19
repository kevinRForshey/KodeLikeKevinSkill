# klk-create-stories

See `sdd-overview.md` for artifact layout and gates before using this file.

**Input**: an approved `docs/sdd/<feature-slug>/spec.md`.
**Output**: `docs/sdd/<feature-slug>/stories.md`.

1. Read `spec.md`. **Refuse to proceed if it has any unresolved
   `NEEDS CLARIFICATION` markers** — name each one exactly, and stop. Don't
   write stories around an unresolved ambiguity.
2. Decompose the spec's `REQ-*` items into independently testable user
   stories — one story can cover one requirement, or a requirement can split
   into several stories if that makes each one independently shippable and
   testable. Every `REQ-*` must be covered by at least one story; every
   story must cite the `REQ-*` ID(s) it implements.
3. Fill this template per story:

   ```markdown
   ## US-001: <short title>
   - **Implements**: REQ-001
   - **Status**: Draft
   - **Priority**: P1 | P2 | P3
   - **Story**: As a <role>, I want <capability>, so that <benefit>.
   - **Acceptance criteria**:
     - **AC-1**: Given <context>, when <action>, then <observable outcome>.
     - **AC-2**: Given <context>, when <action>, then <observable outcome>.
   ```

4. Order stories by priority, P1 first. Don't invent stories that don't
   trace back to a requirement in `spec.md`.
5. Every acceptance criterion must be concrete enough to become one test —
   if you can't phrase a Given/When/Then for it, the story is still too
   vague; narrow it or raise it as a question rather than writing a vague AC.

Report back the full list of story IDs and flag any `REQ-*` that didn't end
up covered by a story — that's a gap, not a silent omission.
