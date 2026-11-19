# klk-create-spec

See `sdd-overview.md` for artifact layout and gates before using this file.

**Input**: a plain-language feature description from the user.
**Output**: `docs/sdd/<feature-slug>/spec.md`.

1. Derive the feature slug from the description; create the directory if
   this is a new feature. If `docs/sdd/<feature-slug>/` already exists,
   this is a revision — read the existing `spec.md` first and update it
   rather than starting over.
2. Fill this template from the description:

   ```markdown
   ---
   title: <Feature Name>
   date_created: <YYYY-MM-DD>
   status: Draft
   ---

   # <Feature Name>

   ## Purpose & Scope
   <What this feature does, who it's for, and what's explicitly out of scope.>

   ## Functional Requirements
   - **REQ-001**: <requirement>
   - **REQ-002**: <requirement>

   ## Constraints
   - **CON-001**: <a technical, business, or regulatory constraint, if any>

   ## Key Entities
   <Only if the feature involves data — name the entities and their
   important fields/relationships. Omit this section otherwise.>

   ## Success Criteria
   - **SC-001**: <an observable, testable outcome>

   ## Assumptions
   <Anything you're assuming because the description didn't say — flag it
   here even if you also marked it NEEDS CLARIFICATION, so it's visible.>
   ```

3. **Mark genuine ambiguities as `NEEDS CLARIFICATION: <specific question>`**
   inline wherever they occur. A requirement is genuinely ambiguous when the
   description doesn't state it and no reasonable default follows from the
   rest of the description — not merely because it wasn't spelled out.
   Never fill a gap with a confident guess.
4. Don't invent requirements, success criteria, or entities the description
   doesn't support, even to make the document look complete. An
   honest-looking `spec.md` with `NEEDS CLARIFICATION` markers is correct
   output; a complete-looking one with guessed content is not.

Report back which REQ/SC items (if any) carry `NEEDS CLARIFICATION` — the
user resolves those before `klk-create-stories` can run.
