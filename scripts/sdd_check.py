#!/usr/bin/env python3
"""Deterministic gate checks for the klk- SDD commands.

Backs the gates described in references/sdd-overview.md with real parsing
instead of asking the model to eyeball markdown. Stdlib only, no deps.

Pipeline: spec.md -> tech-spec.md -> tests (+ tests.md) -> stories.md ->
implementation -> QA.

Subcommands:
  slug <description>
      print the kebab-case feature slug

  gate-clarifications <path>
      exit 1 and list open NEEDS CLARIFICATION items in spec.md or
      tech-spec.md (same marker syntax in both)

  gate-tests <tests.md> --acs AC-1 [AC-2 ...]
      exit 1 if tests.md is missing, or if any named AC-* has zero
      recorded test entries

  gate-stories <stories.md> [--status S [S ...]] [--ids ID [ID ...]]
      print each story's status/AC count; exit 1 if --status given and
      any targeted story doesn't match, or has 0 AC

  set-status <stories.md> <US-ID> <NewStatus>
      rewrite only that story's Status line, after checking the
      transition is a legal single step in the story status machine
      (Ready for Implementation -> Implemented -> Passing, with
      Failing: <reason> reachable from Implemented/Passing and
      recoverable back to Implemented/Passing)
"""
import argparse
import re
import sys

STORY_HEADER_RE = re.compile(r"^## (US-\d+):\s*(.*)$")
STATUS_RE = re.compile(r"^(\s*-\s*\*\*Status\*\*:\s*)(.+?)\s*$")
AC_RE = re.compile(r"^\s*-\s*\*\*AC-\d+\*\*:")
NEEDS_CLARIFICATION_RE = re.compile(
    r"\*\*((?:REQ|CON|SC|TS|AC)-\d+)\*\*:\s*NEEDS CLARIFICATION:\s*(.+?)\s*$"
)
TESTS_AC_HEADER_RE = re.compile(r"^\s*-\s*\*\*(AC-\d+)\*\*")
TESTS_TEST_LINE_RE = re.compile(r"^\s{2,}-\s*Test:")

STORY_STATUS_ORDER = ["Ready for Implementation", "Implemented", "Passing"]


def _is_failing(status: str) -> bool:
    return status.startswith("Failing:")


def _validate_transition(current: str, new: str) -> str | None:
    """Return an error string if current -> new isn't a legal single step, else None."""
    if current == new:
        return None  # re-running a command that already set this status is a no-op
    if _is_failing(new):
        if current in ("Implemented", "Passing") or _is_failing(current):
            return None
        return (
            f"cannot set a Failing status from '{current}' — Failing is only "
            "reachable from 'Implemented', 'Passing', or another Failing state"
        )
    if _is_failing(current):
        if new in ("Implemented", "Passing"):
            return None
        return (
            f"from a Failing state, the only valid next statuses are "
            f"'Implemented' or 'Passing', not '{new}'"
        )
    if current not in STORY_STATUS_ORDER or new not in STORY_STATUS_ORDER:
        return (
            f"unrecognized status '{new}' — expected one of {STORY_STATUS_ORDER} "
            "or 'Failing: <reason>'"
        )
    ci, ni = STORY_STATUS_ORDER.index(current), STORY_STATUS_ORDER.index(new)
    if ci + 1 >= len(STORY_STATUS_ORDER):
        return f"'{current}' has no further forward status"
    if ni != ci + 1:
        return (
            f"cannot jump from '{current}' to '{new}' — next allowed status is "
            f"'{STORY_STATUS_ORDER[ci + 1]}'"
        )
    return None


def cmd_slug(args: argparse.Namespace) -> int:
    slug = re.sub(r"[^a-z0-9]+", "-", args.description.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    print(slug)
    return 0


def _find_open_clarifications(text: str) -> list[str]:
    lines = text.splitlines()
    open_items = []
    for i, line in enumerate(lines):
        m = NEEDS_CLARIFICATION_RE.search(line)
        if not m:
            continue
        question = m.group(2)
        # Markdown wraps long bullet text across lines; merge plain
        # continuation lines (not a new bullet/blank) into the question.
        for cont in lines[i + 1 :]:
            if not cont.strip() or re.match(r"^\s*-\s*\*\*", cont):
                break
            question += " " + cont.strip()
        open_items.append(f"{m.group(1)}: {question}")
    return open_items


def cmd_gate_clarifications(args: argparse.Namespace) -> int:
    open_items = _find_open_clarifications(_read(args.path))
    if open_items:
        print(f"BLOCKED: {len(open_items)} unresolved NEEDS CLARIFICATION item(s):")
        for item in open_items:
            print(f"  - {item}")
        return 1
    print("OK: no unresolved NEEDS CLARIFICATION items")
    return 0


def _parse_tests_manifest(text: str) -> dict[str, int]:
    """Map each AC-* id in tests.md to how many '- Test: ...' lines follow it."""
    counts: dict[str, int] = {}
    current = None
    for line in text.splitlines():
        header = TESTS_AC_HEADER_RE.match(line)
        if header:
            current = header.group(1)
            counts.setdefault(current, 0)
            continue
        if current is not None and TESTS_TEST_LINE_RE.match(line):
            counts[current] += 1
    return counts


def cmd_gate_tests(args: argparse.Namespace) -> int:
    try:
        text = _read(args.tests_path)
    except FileNotFoundError:
        print(f"BLOCKED: no tests manifest found at {args.tests_path}")
        return 1
    counts = _parse_tests_manifest(text)
    missing = [ac for ac in args.acs if counts.get(ac, 0) == 0]
    for ac in args.acs:
        print(f"{ac}: {counts.get(ac, 0)} test(s) recorded")
    if missing:
        print(f"BLOCKED: no recorded test(s) for: {', '.join(missing)}")
        return 1
    print(f"OK: {len(args.acs)} AC(s) each have >=1 recorded test")
    return 0


def _parse_stories(text: str) -> list[dict]:
    stories = []
    current = None
    for line in text.splitlines():
        header = STORY_HEADER_RE.match(line)
        if header:
            current = {
                "id": header.group(1),
                "title": header.group(2),
                "status": None,
                "ac_count": 0,
            }
            stories.append(current)
            continue
        if current is None:
            continue
        status = STATUS_RE.match(line)
        if status:
            current["status"] = status.group(2)
            continue
        if AC_RE.match(line):
            current["ac_count"] += 1
    return stories


def cmd_gate_stories(args: argparse.Namespace) -> int:
    text = _read(args.stories_path)
    stories = _parse_stories(text)
    if not stories:
        print(f"BLOCKED: no '## US-NNN:' story blocks found in {args.stories_path}")
        return 1

    targets = stories
    if args.ids:
        wanted = set(args.ids)
        targets = [s for s in stories if s["id"] in wanted]
        missing = wanted - {s["id"] for s in targets}
        if missing:
            print(f"BLOCKED: story ID(s) not found: {', '.join(sorted(missing))}")
            return 1

    for s in targets:
        print(f"{s['id']} [{s['status']}] AC={s['ac_count']}  {s['title']}")

    if not args.status:
        return 0

    allowed = set(args.status)
    failures = [
        s for s in targets if s["status"] not in allowed or s["ac_count"] == 0
    ]
    if failures:
        print(f"BLOCKED: expected status in {sorted(allowed)} with >=1 AC:")
        for s in failures:
            reason = "no acceptance criteria" if s["ac_count"] == 0 else f"status is {s['status']}"
            print(f"  - {s['id']}: {reason}")
        return 1
    print(f"OK: {len(targets)} story(ies) match required status/AC gate")
    return 0


def cmd_set_status(args: argparse.Namespace) -> int:
    path = args.stories_path
    text = _read(path)
    lines = text.splitlines(keepends=True)

    block_start = None
    for i, line in enumerate(lines):
        header = STORY_HEADER_RE.match(line.rstrip("\n"))
        if header and header.group(1) == args.story_id:
            block_start = i
            continue
        if block_start is not None:
            is_next_header = STORY_HEADER_RE.match(line.rstrip("\n"))
            if is_next_header:
                break
            status = STATUS_RE.match(line.rstrip("\n"))
            if status:
                current_status = status.group(2)
                error = _validate_transition(current_status, args.new_status)
                if error:
                    print(f"BLOCKED: {args.story_id} {error}")
                    return 1
                lines[i] = f"{status.group(1)}{args.new_status}\n"
                with open(path, "w") as f:
                    f.writelines(lines)
                print(f"OK: {args.story_id} status -> {args.new_status}")
                return 0

    print(f"BLOCKED: could not find a Status line for {args.story_id} in {path}")
    return 1


def _read(path: str) -> str:
    with open(path) as f:
        return f.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("slug")
    p.add_argument("description")
    p.set_defaults(func=cmd_slug)

    p = sub.add_parser("gate-clarifications")
    p.add_argument("path")
    p.set_defaults(func=cmd_gate_clarifications)

    p = sub.add_parser("gate-tests")
    p.add_argument("tests_path")
    p.add_argument("--acs", nargs="+", required=True)
    p.set_defaults(func=cmd_gate_tests)

    p = sub.add_parser("gate-stories")
    p.add_argument("stories_path")
    p.add_argument("--status", nargs="+")
    p.add_argument("--ids", nargs="+")
    p.set_defaults(func=cmd_gate_stories)

    p = sub.add_parser("set-status")
    p.add_argument("stories_path")
    p.add_argument("story_id")
    p.add_argument("new_status")
    p.set_defaults(func=cmd_set_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
