#!/usr/bin/env python3
"""Token-budget guard for this skill's own context load.

Progressive disclosure only works if the files actually loaded on each
path stay small — nothing else enforces that. This estimates tokens as
len(text) // 4 (a standard rough estimate; good enough for a ceiling
check, not meant to match any tokenizer exactly) for SKILL.md alone and
for each `klk-` command's full load path (SKILL.md + sdd-overview.md +
that command's own reference file), and fails if any path exceeds its
ceiling.

Run directly to print every path's cost:
  python3 scripts/token_budget.py

Run under the test suite / CI to enforce the ceilings:
  python3 scripts/token_budget.py --check
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Keep these ceilings tight enough to catch regrowth, loose enough not to
# flap on a few words of legitimate added detail.
SKILL_MD_CEILING = 1_300
COMMAND_PATH_CEILING = 3_300

COMMANDS = {
    "klk-create-spec": "sdd-create-spec.md",
    "klk-create-tech-spec": "sdd-create-tech-spec.md",
    "klk-create-tests": "sdd-create-tests.md",
    "klk-create-stories": "sdd-create-stories.md",
    "klk-implement-stories": "sdd-implement-stories.md",
    "klk-run-qa": "sdd-run-qa.md",
    "klk-ship": "sdd-ship.md",
}


def _tokens(text: str) -> int:
    return len(text) // 4


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def compute() -> dict[str, int]:
    skill_md = _tokens(_read("SKILL.md"))
    overview = _tokens(_read("references/sdd-overview.md"))
    paths = {"SKILL.md (bare trigger)": skill_md}
    for command, refname in COMMANDS.items():
        ref = _tokens(_read(f"references/{refname}"))
        paths[command] = skill_md + overview + ref
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if any load path exceeds its ceiling (for CI)",
    )
    args = parser.parse_args()

    paths = compute()
    failed = []
    for name, cost in paths.items():
        ceiling = SKILL_MD_CEILING if name.startswith("SKILL.md") else COMMAND_PATH_CEILING
        flag = "" if cost <= ceiling else f"  OVER ceiling {ceiling}"
        print(f"{cost:6d} tok  {name}{flag}")
        if cost > ceiling:
            failed.append((name, cost, ceiling))

    if args.check and failed:
        print("\nToken budget exceeded:", file=sys.stderr)
        for name, cost, ceiling in failed:
            print(f"  {name}: {cost} > {ceiling}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
