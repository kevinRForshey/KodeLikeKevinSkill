"""Unit tests for scripts/sdd_gate_hook.py.

Invokes the hook as a real subprocess with the same JSON-on-stdin contract
Claude Code uses for a PreToolUse hook, since the whole point of this script
is its behavior under that exact contract -- calling its functions directly
would miss a broken stdin parse or exit code.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK_PATH = str(Path(__file__).resolve().parent.parent / "sdd_gate_hook.py")

SPEC_CLEAN = """\
## Functional requirements
- **REQ-001**: Do the thing.
"""

SPEC_WITH_OPEN_ITEM = """\
## Functional requirements
- **REQ-001**: NEEDS CLARIFICATION: which thing?
"""

TECH_SPEC_FULL = """\
## Technical design items
- **TS-001** [REQ-001]: Do it in the service layer.

## Acceptance criteria
- **AC-1** [REQ-001/TS-001]: Given X, when Y, then Z.
"""

TECH_SPEC_MISSING_AC = """\
## Technical design items
- **TS-001** [REQ-001]: Do it in the service layer.

## Acceptance criteria
"""

TECH_SPEC_WITH_OPEN_ITEM = """\
## Technical design items
- **TS-001**: NEEDS CLARIFICATION: which layer?

## Acceptance criteria
- **AC-1** [REQ-001/TS-001]: Given X, when Y, then Z.
"""

TESTS_MANIFEST = """\
- **AC-1**
  - Test: test_thing_happens
"""

STORIES_ALL_PASSING = """\
## US-001: Do the thing
- **Covers**: AC-1 (REQ-001/TS-001)
- **Status**: Passing
"""

STORIES_ONE_NOT_PASSING = """\
## US-001: Do the thing
- **Covers**: AC-1 (REQ-001/TS-001)
- **Status**: Implemented
"""

STORIES_MISSING_AC_COVERAGE = """\
## US-001: Unrelated story
- **Covers**: AC-2 (REQ-002/TS-002)
- **Status**: Passing
"""


def run_hook(tool_name: str, file_path: str, content: str = "") -> subprocess.CompletedProcess:
    payload = {
        "tool_name": tool_name,
        "tool_input": {"file_path": file_path, "content": content},
        "cwd": os.getcwd(),
    }
    return subprocess.run(
        [sys.executable, HOOK_PATH],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


def run_hook_raw(stdin_text: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, HOOK_PATH],
        input=stdin_text,
        capture_output=True,
        text=True,
    )


class MalformedInputFailsOpenCleanly(unittest.TestCase):
    def test_empty_stdin_exits_zero_with_no_traceback(self):
        result = run_hook_raw("")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def test_malformed_json_exits_zero_with_no_traceback(self):
        result = run_hook_raw("not json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def test_non_object_json_exits_zero(self):
        result = run_hook_raw("[1, 2, 3]")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def test_tool_input_not_an_object_exits_zero(self):
        result = run_hook_raw('{"tool_name": "Write", "tool_input": "oops"}')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def test_file_path_not_a_string_exits_zero(self):
        result = run_hook_raw(
            '{"tool_name": "Write", "tool_input": {"file_path": 123}}'
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")


class NonMatchingPathsAreAllowed(unittest.TestCase):
    def test_unrelated_file_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_hook("Write", str(Path(tmp) / "src" / "main.py"))
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")

    def test_spec_md_itself_is_allowed_unconditionally(self):
        with tempfile.TemporaryDirectory() as tmp:
            slug_dir = Path(tmp) / "docs" / "sdd" / "my-feature"
            slug_dir.mkdir(parents=True)
            result = run_hook("Write", str(slug_dir / "spec.md"))
            self.assertEqual(result.returncode, 0)

    def test_non_write_edit_tool_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            slug_dir = Path(tmp) / "docs" / "sdd" / "my-feature"
            slug_dir.mkdir(parents=True)
            result = run_hook("Read", str(slug_dir / "tech-spec.md"))
            self.assertEqual(result.returncode, 0)


class TechSpecGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.slug_dir = Path(self.tmp.name) / "docs" / "sdd" / "my-feature"
        self.slug_dir.mkdir(parents=True)
        self.target = str(self.slug_dir / "tech-spec.md")

    def tearDown(self):
        self.tmp.cleanup()

    def test_blocks_when_spec_missing(self):
        result = run_hook("Write", self.target)
        self.assertEqual(result.returncode, 2)
        self.assertIn("spec.md doesn't exist", result.stderr)

    def test_blocks_when_spec_has_open_clarification(self):
        (self.slug_dir / "spec.md").write_text(SPEC_WITH_OPEN_ITEM)
        result = run_hook("Write", self.target)
        self.assertEqual(result.returncode, 2)
        self.assertIn("NEEDS CLARIFICATION", result.stderr)

    def test_allows_when_spec_is_clean(self):
        (self.slug_dir / "spec.md").write_text(SPEC_CLEAN)
        result = run_hook("Write", self.target)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def test_edit_tool_is_gated_the_same_as_write(self):
        result = run_hook("Edit", self.target)
        self.assertEqual(result.returncode, 2)


class TestsGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.slug_dir = Path(self.tmp.name) / "docs" / "sdd" / "my-feature"
        self.slug_dir.mkdir(parents=True)
        self.target = str(self.slug_dir / "tests.md")

    def tearDown(self):
        self.tmp.cleanup()

    def test_blocks_when_tech_spec_missing(self):
        result = run_hook("Write", self.target)
        self.assertEqual(result.returncode, 2)
        self.assertIn("tech-spec.md doesn't exist", result.stderr)

    def test_blocks_when_tech_spec_has_open_clarification(self):
        (self.slug_dir / "tech-spec.md").write_text(TECH_SPEC_WITH_OPEN_ITEM)
        result = run_hook("Write", self.target)
        self.assertEqual(result.returncode, 2)
        self.assertIn("NEEDS CLARIFICATION", result.stderr)

    def test_blocks_when_req_coverage_incomplete(self):
        (self.slug_dir / "spec.md").write_text(SPEC_CLEAN)
        (self.slug_dir / "tech-spec.md").write_text(TECH_SPEC_MISSING_AC)
        result = run_hook("Write", self.target)
        self.assertEqual(result.returncode, 2)
        self.assertIn("REQ-001", result.stderr)

    def test_allows_when_fully_covered(self):
        (self.slug_dir / "spec.md").write_text(SPEC_CLEAN)
        (self.slug_dir / "tech-spec.md").write_text(TECH_SPEC_FULL)
        result = run_hook("Write", self.target)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")


class StoriesGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.slug_dir = Path(self.tmp.name) / "docs" / "sdd" / "my-feature"
        self.slug_dir.mkdir(parents=True)
        self.target = str(self.slug_dir / "stories.md")

    def tearDown(self):
        self.tmp.cleanup()

    def test_blocks_when_tests_manifest_missing(self):
        result = run_hook("Write", self.target)
        self.assertEqual(result.returncode, 2)
        self.assertIn("tests.md doesn't exist", result.stderr)

    def test_blocks_when_tests_manifest_is_empty(self):
        (self.slug_dir / "tests.md").write_text("   \n")
        result = run_hook("Write", self.target)
        self.assertEqual(result.returncode, 2)

    def test_allows_when_tests_manifest_present(self):
        (self.slug_dir / "tests.md").write_text(TESTS_MANIFEST)
        result = run_hook("Write", self.target)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")


class PrDescriptionGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.slug_dir = Path(self.tmp.name) / "docs" / "sdd" / "my-feature"
        self.slug_dir.mkdir(parents=True)
        self.target = str(self.slug_dir / "pr-description.md")

    def tearDown(self):
        self.tmp.cleanup()

    def test_blocks_when_tech_spec_or_stories_missing(self):
        result = run_hook("Write", self.target)
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing tech-spec.md", result.stderr)

    def test_blocks_when_an_ac_has_no_story(self):
        (self.slug_dir / "tech-spec.md").write_text(TECH_SPEC_FULL)
        (self.slug_dir / "stories.md").write_text(STORIES_MISSING_AC_COVERAGE)
        result = run_hook("Write", self.target)
        self.assertEqual(result.returncode, 2)
        self.assertIn("AC-1", result.stderr)

    def test_blocks_when_a_story_is_not_passing(self):
        (self.slug_dir / "tech-spec.md").write_text(TECH_SPEC_FULL)
        (self.slug_dir / "stories.md").write_text(STORIES_ONE_NOT_PASSING)
        result = run_hook("Write", self.target)
        self.assertEqual(result.returncode, 2)
        self.assertIn("not Passing", result.stderr)

    def test_allows_when_fully_covered_and_passing(self):
        (self.slug_dir / "tech-spec.md").write_text(TECH_SPEC_FULL)
        (self.slug_dir / "stories.md").write_text(STORIES_ALL_PASSING)
        result = run_hook("Write", self.target)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
