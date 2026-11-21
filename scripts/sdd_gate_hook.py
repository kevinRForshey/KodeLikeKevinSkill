#!/usr/bin/env python3
"""Claude Code PreToolUse hook: mechanically enforce the klk- SDD gate chain.

Without this hook, nothing stops an agent from writing tech-spec.md/tests.md/
stories.md without ever running the gate-* subcommand its own instructions
tell it to run first -- the gate is only as real as the agent's compliance.
This hook makes the gate unconditional: it reads the same spec.md/tech-spec.md
the gate-* commands read and blocks the Write/Edit outright when a
prerequisite isn't met, regardless of whether the agent ran a gate check.

Wire it into .claude/settings.json (project-level, so it only applies to
projects that opt in):

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

Reads the PreToolUse JSON payload Claude Code pipes to stdin (fields
tool_name, tool_input.file_path) per https://code.claude.com/docs/en/hooks.md.
Any file that isn't docs/sdd/<slug>/{tech-spec,tests,stories,pr-description}.md
is allowed unconditionally (exit 0) -- this only guards the SDD planning
chain itself, never arbitrary project files, so it's safe to enable broadly.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

_SDD_CHECK_PATH = Path(__file__).resolve().parent / "sdd_check.py"
_spec = importlib.util.spec_from_file_location("sdd_check", _SDD_CHECK_PATH)
assert _spec is not None and _spec.loader is not None
sdd_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sdd_check)

ARTIFACT_RE = re.compile(r"docs/sdd/[^/]+/(tech-spec|tests|stories|pr-description)\.md$")


def _read_or_none(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def _block(reason: str) -> None:
    print(reason, file=sys.stderr)
    sys.exit(2)


def _check_tech_spec(directory: Path) -> None:
    spec_text = _read_or_none(directory / "spec.md")
    if spec_text is None:
        _block(
            f"BLOCKED by sdd_gate_hook: {directory}/spec.md doesn't exist "
            "yet -- run klk-create-spec before klk-create-tech-spec."
        )
    open_items = sdd_check._find_open_clarifications(spec_text)
    if open_items:
        _block(
            "BLOCKED by sdd_gate_hook: spec.md has unresolved "
            "NEEDS CLARIFICATION markers -- resolve them before writing "
            "tech-spec.md:\n- " + "\n- ".join(open_items)
        )


def _check_tests(directory: Path) -> None:
    tech_spec_text = _read_or_none(directory / "tech-spec.md")
    if tech_spec_text is None:
        _block(
            f"BLOCKED by sdd_gate_hook: {directory}/tech-spec.md doesn't "
            "exist yet -- run klk-create-tech-spec before klk-create-tests."
        )
    open_items = sdd_check._find_open_clarifications(tech_spec_text)
    if open_items:
        _block(
            "BLOCKED by sdd_gate_hook: tech-spec.md has unresolved "
            "NEEDS CLARIFICATION markers -- resolve them before writing "
            "tests.md:\n- " + "\n- ".join(open_items)
        )
    spec_text = _read_or_none(directory / "spec.md") or ""
    reqs = sdd_check._parse_defined_req_ids(spec_text)
    ts_covered, ac_covered = sdd_check._parse_req_coverage(tech_spec_text)
    missing = [r for r in reqs if r not in ts_covered or r not in ac_covered]
    if missing:
        _block(
            "BLOCKED by sdd_gate_hook: tech-spec.md doesn't cover every "
            "REQ-* with >=1 TS-* and >=1 AC-* yet -- missing: "
            + ", ".join(missing)
        )


def _check_stories(directory: Path) -> None:
    tests_text = _read_or_none(directory / "tests.md")
    if tests_text is None or not tests_text.strip():
        _block(
            f"BLOCKED by sdd_gate_hook: {directory}/tests.md doesn't exist "
            "yet (or is empty) -- run klk-create-tests before "
            "klk-create-stories."
        )


def _check_pr_description(directory: Path) -> None:
    tech_spec_text = _read_or_none(directory / "tech-spec.md")
    stories_text = _read_or_none(directory / "stories.md")
    if tech_spec_text is None or stories_text is None:
        _block(
            f"BLOCKED by sdd_gate_hook: {directory} is missing tech-spec.md "
            "or stories.md -- klk-ship needs both before drafting "
            "pr-description.md."
        )
    acs = sdd_check._parse_defined_ac_ids(tech_spec_text)
    stories = sdd_check._parse_stories(stories_text)
    covered = {ac for s in stories for ac in s["covers_ac"]}
    missing_ac = [ac for ac in acs if ac not in covered]
    if missing_ac:
        _block(
            "BLOCKED by sdd_gate_hook: AC(s) not covered by any story -- "
            "run klk-create-stories first: " + ", ".join(missing_ac)
        )
    not_passing = [s for s in stories if s["status"] != "Passing"]
    if not_passing:
        _block(
            "BLOCKED by sdd_gate_hook: story(ies) not Passing yet -- "
            "run klk-implement-stories/klk-run-qa first: "
            + ", ".join(f"{s['id']} ({s['status']})" for s in not_passing)
        )


_CHECKS = {
    "tech-spec": _check_tech_spec,
    "tests": _check_tests,
    "stories": _check_stories,
    "pr-description": _check_pr_description,
}


def _run(payload: object) -> None:
    if not isinstance(payload, dict) or payload.get("tool_name") not in ("Write", "Edit"):
        return
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return
    file_path = tool_input.get("file_path")
    if not isinstance(file_path, str):
        return
    normalized = file_path.replace("\\", "/")
    m = ARTIFACT_RE.search(normalized)
    if not m:
        return
    _CHECKS[m.group(1)](Path(file_path).resolve().parent)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        _run(payload)
    except SystemExit:
        raise  # a real gate block (_block() calls sys.exit(2)) -- let it propagate
    except Exception:
        # Any payload shape we didn't anticipate (not stdlib-documented, a
        # future Claude Code version, etc.) fails open rather than blocking
        # an unrelated Write/Edit on our own malfunction. This isn't a
        # security control -- a silent allow beats bricking the project.
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
