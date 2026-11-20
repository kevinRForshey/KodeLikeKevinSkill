# klk-create-tech-spec

See `sdd-overview.md` for artifact layout and gates before using this file.
This command turns an approved **what** (`spec.md`) into a **how**
(`tech-spec.md`) — and writes the acceptance criteria that `klk-create-tests`
will turn directly into tests. No test code and no production code here.

**Input**: an approved `docs/sdd/<feature-slug>/spec.md`.
**Output**: `docs/sdd/<feature-slug>/tech-spec.md`.

1. Run `python3 scripts/sdd_check.py gate-clarifications docs/sdd/<feature-slug>/spec.md`
   first. **Refuse to proceed on exit 1** — name each listed item exactly,
   and stop. Don't design against an unresolved ambiguity. Then read
   `spec.md` itself for content.
2. Fill this template:

   ```markdown
   ---
   title: <Feature Name> — Technical Spec
   date_created: <YYYY-MM-DD>
   status: Draft
   ---

   # <Feature Name> — Technical Spec

   ## Design overview
   <The technical approach in a few sentences: what components/layers
   change, and why this approach over an obvious alternative, if one
   existed.>

   ## Technical design items
   - **TS-001**: <a concrete technical decision — a data model/schema
     change, an interface/contract, a component boundary> — implements
     REQ-00N.
   - **TS-002**: <...> — implements REQ-00N.

   ## Acceptance criteria
   - **AC-1**: Given <context>, when <action>, then <observable outcome>.
     — implements REQ-00N / TS-00N.
   - **AC-2**: Given <context>, when <action>, then <observable outcome>.
     — implements REQ-00N / TS-00N.

   ## Non-functional notes
   <Only if the spec's CON-* items imply a technical consequence —
   performance, security boundary, data-residency handling. Omit otherwise.>
   ```

3. **Every `REQ-*` in `spec.md` must be covered by at least one `TS-*` and
   at least one `AC-*`.** A requirement can expand into several AC (happy
   path, guard/error cases) — this is deliberate: `klk-create-tests` writes
   one test per `AC-*`, so an AC too coarse to phrase as one test is too
   coarse to carry forward.
4. Mark genuine ambiguities that `spec.md` didn't resolve as
   `NEEDS CLARIFICATION: <specific question>` on the relevant `TS-*`/`AC-*`
   — these are *technical* ambiguities spec-level clarification wouldn't
   have caught (e.g. "which existing service owns this?", "synchronous or
   queued?"). Never fill a technical gap with a confident guess.
5. Don't invent technical items or AC that don't trace back to a `REQ-*`.
   An honest-looking `tech-spec.md` with `NEEDS CLARIFICATION` markers is
   correct output; a complete-looking one with guessed content is not.
6. Run `python3 scripts/sdd_check.py gate-clarifications docs/sdd/<feature-slug>/tech-spec.md`
   and report its result directly.

Report back the full `TS-*`/`AC-*` list, confirm every `spec.md` `REQ-*` is
covered, and flag any `NEEDS CLARIFICATION` — the user resolves those before
`klk-create-tests` can run.
