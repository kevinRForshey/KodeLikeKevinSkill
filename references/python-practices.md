# Python Practices

Detail for the "References" pointer in `skill.md`. No specialized skill is
currently installed for Python, so this skill owns these conventions
directly.

## Naming
- **snake_case** — functions, variables, modules, packages.
- **PascalCase** — classes.
- **UPPER_SNAKE_CASE** — module-level constants.
- **_leading_underscore** — internal/non-public names (PEP 8); reserve
  dunder names (`__init__`, etc.) for actual special methods.

## PEP 8 / style
- Follow PEP 8. Defer to the project's formatter (black, ruff format) if one
  is configured, rather than hand-formatting to match it.
- Use f-strings for interpolation, not `%` formatting or `.format()`.
- Use explicit dependency/environment management (venv, poetry, or uv) —
  match whatever the project already uses rather than introducing a second
  tool into it.

## Typing
- Add type hints to every public function/method signature (params and
  return type); keep the codebase mypy-clean wherever the project already
  uses typing.
- Prefer PEP 604 `X | None` union syntax over `Optional[X]` on Python ≥3.10
  projects.
- Use `dataclasses` (or `pydantic` models where validation is needed) for
  data-carrying types over plain dicts/tuples passed around as pseudo-records.
- For FastAPI (or similar) request/response schemas specifically, use
  Pydantic models, not raw dicts.

## Docstrings (PEP 257)
- Every public module, class, and function gets a docstring: one summary
  line, a blank line, then `Args:`/`Returns:`/`Raises:` sections (Google or
  NumPy style — match whatever the project already uses).

## Testing
- **pytest** — plain `assert` statements, fixtures for setup/teardown,
  `pytest.mark.parametrize` for data-driven cases rather than hand-rolled
  loops.
- Cover both happy-path and failing/error cases. If no test setup exists
  yet, create one and backfill tests for anything currently untested.

## Data/signal-processing pipelines (e.g. EEG/EDF)
- Be explicit about units, sample rates, and array shapes in docstrings or
  type hints — silent shape mismatches are a classic source of subtle bugs
  in this domain.

## The Zen of Python, applied literally
Treat `import this` as a real design checklist, not a slogan:
- *Explicit is better than implicit* — no `from x import *`; no magic
  attribute injection.
- *Simple is better than complex. Complex is better than complicated* — this
  is YAGNI/KISS in Python's own words.
- *Flat is better than nested* — prefer early returns/guard clauses over deep
  nesting.
- *There should be one — and preferably only one — obvious way to do it* —
  don't introduce a second idiom for something the stdlib already does one
  obvious way.
- *Errors should never pass silently* — no bare `except:` swallowing
  exceptions.
