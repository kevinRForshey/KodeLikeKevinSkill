---
name: kode-like-kevin-dotnet
description:  .NET (C#, Blazor, ASP.NET Core) engineering conventions and klk-prefixed spec-driven development (SDD) workflow. Use when writing, editing, reviewing, or scaffolding .NET code or tests, enforcing SOLID/YAGNI/Repository conventions, or running klk-* SDD commands (klk-create-spec, klk-create-tech-spec, klk-create-tests, klk-create-stories, klk-implement-stories, klk-run-qa, klk-ship).
---

# .NET Engineering Conventions & SDD Workflow

Apply to C#, Blazor (`.razor`), ASP.NET Core, and `.csproj`/`.sln` work unless the repository's `CLAUDE.md` or a project-scoped skill specifies otherwise (project-level conventions always win). The separate `kodelikekevin` skill's rules 1-9 (senior-engineer stance, plan-first, validate-before-done, YAGNI, SOLID-without-stuffing, documentation-on-change, token efficiency, attribution) apply here unchanged — everything below is only the .NET/Blazor/SDD-specific addition on top.

## Routing & Scope
- **Defer to specialized skills naturally:** Do not preload specialized .NET skills upfront. Only load them when the active file or task specifically requires them.
- **Compete check:** If the target repo already has a `.specify` scaffold and an installed spec-kit lifecycle skill (such as `mds-` commands), defer to that instead of `klk-` commands.
- **Process governance (`ai-governance`):** Apply `ai-governance` alongside this skill without duplicating work:
  - Approved `tech-spec.md` + `stories.md` artifacts satisfy **Gate 0 (Analyze & Plan)**—do not re-plan per story during `klk-implement-stories`.
  - Run coverage-tool verification (**Gate 1 / Gate 3: 90% floor via exit code**) once in `klk-run-qa` (or final verification), not after every individual story edit.

## Version Control Policy
Never run `git commit` or `git push` unless explicitly requested for that specific action in the current turn. Read-only inspection (`status`, `diff`, `log`), staging, and local branching do not require asking. Approval is scoped to the requested action only—never treat it as standing permission.

## SDD-Specific Token Discipline
- **One SDD phase per session:** Never run all seven `klk-` commands in a single continuous thread. Persist state to disk (`spec.md`, `tech-spec.md`, `tests.md`, `stories.md`), validate via `scripts/sdd_check.py`, and stop at the phase boundary so the user can `/clear` (or run the next stage in a fresh session).
- **Load references on demand:** Read only the single reference file matching the active `klk-` command, or `references/csharp-dotnet-practices.md` when needed — never the whole `references/` directory.
- **Compress `.NET` CLI output:** Never dump full `dotnet build`, `dotnet test`, or coverage logs into context—surface only compiler errors, failing test assertions, and exit codes, and reuse `--no-restore` / `--no-build` during iterative inner loops when appropriate.

## .NET Engineering Principles
- **Data access:** Isolate persistence behind the **Repository pattern** with intent-revealing methods; do not leak `IQueryable<T>` or raw ORM query objects across service/business boundaries.
- **Testing:** Add unit/integration tests covering happy paths and guard/failure cases using the test framework already present in the solution (defaulting to xUnit only when no test project exists).

## Documentation (on top of `kodelikekevin` rule 7)
- **Public APIs:** Update C# XML doc comments and OpenAPI/Swagger annotations in the same change (`references/documentation.md`).
- **Blazor UI changes:** Update user documentation under `docs/user/` (`references/documentation.md`).

## Spec-Driven Development (`klk-` Commands)
Each command reads the prior stage's artifact, enforces mechanical gates via `scripts/sdd_check.py` (never by eye), and halts immediately if a gate fails. Read `references/sdd-overview.md` plus **only** the reference file for the single command invoked:

| Command | Input | Output Artifact | Reference |
|---|---|---|---|
| `klk-create-spec` | Feature description | `spec.md` | `references/sdd-create-spec.md` |
| `klk-create-tech-spec` | Approved `spec.md` | `tech-spec.md` | `references/sdd-create-tech-spec.md` |
| `klk-create-tests` | Approved `tech-spec.md` | Failing tests + `tests.md` | `references/sdd-create-tests.md` |
| `klk-create-stories` | `tests.md` | `stories.md` | `references/sdd-create-stories.md` |
| `klk-implement-stories` | Ready stories | Passing C# code | `references/sdd-implement-stories.md` |
| `klk-run-qa` | Implemented stories | Test + 90% coverage report | `references/sdd-run-qa.md` |
| `klk-ship` | `Passing` stories | `pr-description.md` + staged diff | `references/sdd-ship.md` |

**Pipeline execution rule:** If asked to "run the full SDD workflow for X," run **only the next incomplete stage** determined by existing artifacts on disk, validate it with `scripts/sdd_check.py`, report the artifact path, and prompt the user to `/clear` before continuing to the next stage (or run each stage via an isolated `claude -p "/klk-..."` step).

## .NET References (Load Only When Needed)
- `references/csharp-dotnet-practices.md`
- `references/documentation.md`
