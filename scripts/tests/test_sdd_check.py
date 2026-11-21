"""Unit tests for scripts/sdd_check.py — the gate script every klk- command
trusts. Stdlib unittest only, no deps, matching the script's own constraint.

Run: python3 -m unittest discover -s scripts/tests
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

SDD_CHECK_PATH = os.path.join(os.path.dirname(__file__), "..", "sdd_check.py")
_spec = importlib.util.spec_from_file_location("sdd_check", SDD_CHECK_PATH)
assert _spec is not None and _spec.loader is not None
sdd_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sdd_check)


def write_tmp(content: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".md")
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


class SlugTests(unittest.TestCase):
    def test_slug_derivation(self):
        import argparse
        import io
        import contextlib

        args = argparse.Namespace(description="Cancel an Order!! (v2)")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sdd_check.cmd_slug(args)
        self.assertEqual(buf.getvalue().strip(), "cancel-an-order-v2")


class ClarificationGateTests(unittest.TestCase):
    def test_clean_file_has_no_open_items(self):
        text = "## Functional Requirements\n- **REQ-001**: Users can log in.\n"
        self.assertEqual(sdd_check._find_open_clarifications(text), [])

    def test_flags_each_marker_prefix(self):
        text = (
            "- **REQ-001**: NEEDS CLARIFICATION: which users?\n"
            "- **CON-001**: NEEDS CLARIFICATION: what limit?\n"
            "- **TS-001**: NEEDS CLARIFICATION: which service owns this?\n"
            "- **AC-001**: NEEDS CLARIFICATION: what's the exact timeout?\n"
        )
        items = sdd_check._find_open_clarifications(text)
        self.assertEqual(len(items), 4)
        self.assertTrue(items[0].startswith("REQ-001:"))
        self.assertTrue(items[2].startswith("TS-001:"))

    def test_merges_wrapped_continuation_lines(self):
        text = (
            "- **REQ-002**: NEEDS CLARIFICATION: Which data,\n"
            "  specifically? Profile fields or order history?\n"
            "- **REQ-003**: fine.\n"
        )
        items = sdd_check._find_open_clarifications(text)
        self.assertEqual(len(items), 1)
        self.assertIn("Profile fields or order history?", items[0])

    def test_continuation_merge_stops_at_heading_with_no_blank_line(self):
        text = (
            "- **REQ-001**: NEEDS CLARIFICATION: which users?\n"
            "## Constraints\n"
            "- **CON-001**: fine.\n"
        )
        items = sdd_check._find_open_clarifications(text)
        self.assertEqual(items, ["REQ-001: which users?"])

    def test_gate_clarifications_cli_exit_codes(self):
        import argparse

        clean = write_tmp("- **REQ-001**: fine.\n")
        blocked = write_tmp("- **REQ-001**: NEEDS CLARIFICATION: eh?\n")
        try:
            self.assertEqual(
                sdd_check.cmd_gate_clarifications(argparse.Namespace(path=clean)), 0
            )
            self.assertEqual(
                sdd_check.cmd_gate_clarifications(argparse.Namespace(path=blocked)), 1
            )
        finally:
            os.remove(clean)
            os.remove(blocked)

    def test_gate_clarifications_missing_file_blocks_cleanly(self):
        import argparse

        rc = sdd_check.cmd_gate_clarifications(
            argparse.Namespace(path="/no/such/spec.md")
        )
        self.assertEqual(rc, 1)


class CoverageGateTests(unittest.TestCase):
    SPEC = (
        "## Functional Requirements\n"
        "- **REQ-001**: Users can log in.\n"
        "- **REQ-002**: Sessions expire.\n"
    )
    TECH_SPEC_FULL = (
        "## Technical design items\n"
        "- **TS-001** [REQ-001]: Login endpoint.\n"
        "- **TS-002** [REQ-002]: Expiry job.\n"
        "## Acceptance criteria\n"
        "- **AC-1** [REQ-001/TS-001]: Given X, when Y, then Z.\n"
        "- **AC-2** [REQ-002/TS-002]: Given X, when Y, then Z.\n"
    )
    TECH_SPEC_MISSING_AC = (
        "## Technical design items\n"
        "- **TS-001** [REQ-001]: Login endpoint.\n"
        "- **TS-002** [REQ-002]: Expiry job.\n"
        "## Acceptance criteria\n"
        "- **AC-1** [REQ-001/TS-001]: Given X, when Y, then Z.\n"
    )
    TECH_SPEC_MISSING_TS = (
        "## Acceptance criteria\n"
        "- **AC-1** [REQ-001]: Given X, when Y, then Z.\n"
        "- **AC-2** [REQ-002]: Given X, when Y, then Z.\n"
    )

    def test_parses_defined_req_ids(self):
        self.assertEqual(
            sdd_check._parse_defined_req_ids(self.SPEC), ["REQ-001", "REQ-002"]
        )

    def test_parses_ts_and_ac_coverage_separately(self):
        ts_covered, ac_covered = sdd_check._parse_req_coverage(
            self.TECH_SPEC_MISSING_AC
        )
        self.assertEqual(ts_covered, {"REQ-001", "REQ-002"})
        self.assertEqual(ac_covered, {"REQ-001"})

    def test_gate_passes_when_every_req_has_ts_and_ac(self):
        import argparse

        spec = write_tmp(self.SPEC)
        tech = write_tmp(self.TECH_SPEC_FULL)
        try:
            rc = sdd_check.cmd_gate_coverage(
                argparse.Namespace(spec_path=spec, tech_spec_path=tech)
            )
            self.assertEqual(rc, 0)
        finally:
            os.remove(spec)
            os.remove(tech)

    def test_gate_blocks_when_a_req_has_no_ac(self):
        import argparse

        spec = write_tmp(self.SPEC)
        tech = write_tmp(self.TECH_SPEC_MISSING_AC)
        try:
            rc = sdd_check.cmd_gate_coverage(
                argparse.Namespace(spec_path=spec, tech_spec_path=tech)
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(spec)
            os.remove(tech)

    def test_gate_blocks_when_a_req_has_no_ts(self):
        import argparse

        spec = write_tmp(self.SPEC)
        tech = write_tmp(self.TECH_SPEC_MISSING_TS)
        try:
            rc = sdd_check.cmd_gate_coverage(
                argparse.Namespace(spec_path=spec, tech_spec_path=tech)
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(spec)
            os.remove(tech)

    def test_gate_blocks_on_missing_spec_file(self):
        import argparse

        tech = write_tmp(self.TECH_SPEC_FULL)
        try:
            rc = sdd_check.cmd_gate_coverage(
                argparse.Namespace(spec_path="/no/such/spec.md", tech_spec_path=tech)
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(tech)

    def test_gate_blocks_on_missing_tech_spec_file(self):
        import argparse

        spec = write_tmp(self.SPEC)
        try:
            rc = sdd_check.cmd_gate_coverage(
                argparse.Namespace(
                    spec_path=spec, tech_spec_path="/no/such/tech-spec.md"
                )
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(spec)

    def test_gate_blocks_on_spec_with_no_req_bullets(self):
        import argparse

        spec = write_tmp("## Functional Requirements\n<nothing yet>\n")
        tech = write_tmp(self.TECH_SPEC_FULL)
        try:
            rc = sdd_check.cmd_gate_coverage(
                argparse.Namespace(spec_path=spec, tech_spec_path=tech)
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(spec)
            os.remove(tech)


class TestsManifestGateTests(unittest.TestCase):
    MANIFEST = (
        "# Feature — Tests (Definition of Done)\n\n"
        "- **AC-1** [REQ-001]: Given X, when Y, then Z.\n"
        "  - Test: `tests/Foo.cs::Does_X` — red\n"
        "  - Test: `tests/Foo.cs::Does_X_Guard` — red\n"
        "- **AC-2** [REQ-001]: Given A, when B, then C.\n"
        "  - Test: `tests/Foo.cs::Does_B` — red\n"
        "- **AC-3** [REQ-002]: Given nothing written yet.\n"
    )

    def test_parses_test_counts_per_ac(self):
        counts = sdd_check._parse_tests_manifest(self.MANIFEST)
        self.assertEqual(counts["AC-1"], 2)
        self.assertEqual(counts["AC-2"], 1)
        self.assertEqual(counts["AC-3"], 0)

    def test_gate_passes_when_every_requested_ac_has_a_test(self):
        import argparse

        path = write_tmp(self.MANIFEST)
        try:
            rc = sdd_check.cmd_gate_tests(
                argparse.Namespace(tests_path=path, acs=["AC-1", "AC-2"])
            )
            self.assertEqual(rc, 0)
        finally:
            os.remove(path)

    def test_gate_blocks_on_ac_with_zero_tests(self):
        import argparse

        path = write_tmp(self.MANIFEST)
        try:
            rc = sdd_check.cmd_gate_tests(
                argparse.Namespace(tests_path=path, acs=["AC-1", "AC-3"])
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(path)

    def test_gate_blocks_when_manifest_missing(self):
        import argparse

        rc = sdd_check.cmd_gate_tests(
            argparse.Namespace(tests_path="/no/such/tests.md", acs=["AC-1"])
        )
        self.assertEqual(rc, 1)


class StoriesGateTests(unittest.TestCase):
    STORIES = (
        "## US-001: First story\n"
        "- **Status**: Ready for Implementation\n"
        "- **Acceptance criteria**:\n"
        "  - **AC-1**: Given X, when Y, then Z.\n"
        "## US-002: Second story, no AC\n"
        "- **Status**: Implemented\n"
    )

    def test_parses_status_and_ac_count(self):
        stories = sdd_check._parse_stories(self.STORIES)
        self.assertEqual(stories[0]["status"], "Ready for Implementation")
        self.assertEqual(stories[0]["ac_count"], 1)
        self.assertEqual(stories[1]["ac_count"], 0)

    def test_gate_blocks_on_wrong_status(self):
        import argparse

        path = write_tmp(self.STORIES)
        try:
            rc = sdd_check.cmd_gate_stories(
                argparse.Namespace(
                    stories_path=path, ids=["US-001"], status=["Implemented"]
                )
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(path)

    def test_gate_blocks_on_zero_acceptance_criteria(self):
        import argparse

        path = write_tmp(self.STORIES)
        try:
            rc = sdd_check.cmd_gate_stories(
                argparse.Namespace(
                    stories_path=path,
                    ids=["US-002"],
                    status=["Implemented"],
                )
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(path)

    def test_gate_blocks_on_unknown_id(self):
        import argparse

        path = write_tmp(self.STORIES)
        try:
            rc = sdd_check.cmd_gate_stories(
                argparse.Namespace(stories_path=path, ids=["US-999"], status=None)
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(path)

    def test_gate_passes_for_matching_status_and_ac(self):
        import argparse

        path = write_tmp(self.STORIES)
        try:
            rc = sdd_check.cmd_gate_stories(
                argparse.Namespace(
                    stories_path=path,
                    ids=["US-001"],
                    status=["Ready for Implementation"],
                )
            )
            self.assertEqual(rc, 0)
        finally:
            os.remove(path)

    def test_gate_stories_missing_file_blocks_cleanly(self):
        import argparse

        rc = sdd_check.cmd_gate_stories(
            argparse.Namespace(stories_path="/no/such/stories.md", ids=None, status=None)
        )
        self.assertEqual(rc, 1)


class ShipGateTests(unittest.TestCase):
    TECH_SPEC = (
        "## Acceptance criteria\n"
        "- **AC-1** [REQ-001/TS-001]: Given X, when Y, then Z.\n"
        "- **AC-2** [REQ-002/TS-002]: Given A, when B, then C.\n"
    )
    STORIES_ALL_PASSING = (
        "## US-001: First story\n"
        "- **Covers**: AC-1 (REQ-001/TS-001)\n"
        "- **Status**: Passing\n"
        "## US-002: Second story\n"
        "- **Covers**: AC-2 (REQ-002/TS-002)\n"
        "- **Status**: Passing\n"
    )
    STORIES_ONE_NOT_PASSING = (
        "## US-001: First story\n"
        "- **Covers**: AC-1 (REQ-001/TS-001)\n"
        "- **Status**: Passing\n"
        "## US-002: Second story\n"
        "- **Covers**: AC-2 (REQ-002/TS-002)\n"
        "- **Status**: Implemented\n"
    )
    STORIES_MISSING_AC_COVERAGE = (
        "## US-001: First story\n"
        "- **Covers**: AC-1 (REQ-001/TS-001)\n"
        "- **Status**: Passing\n"
    )

    def test_parses_covers_line_into_ac_set(self):
        stories = sdd_check._parse_stories(self.STORIES_ALL_PASSING)
        self.assertEqual(stories[0]["covers_ac"], {"AC-1"})
        self.assertEqual(stories[1]["covers_ac"], {"AC-2"})

    def test_parses_defined_ac_ids_from_tech_spec(self):
        self.assertEqual(
            sdd_check._parse_defined_ac_ids(self.TECH_SPEC), ["AC-1", "AC-2"]
        )

    def test_gate_passes_when_every_ac_covered_and_all_passing(self):
        import argparse

        tech = write_tmp(self.TECH_SPEC)
        stories = write_tmp(self.STORIES_ALL_PASSING)
        try:
            rc = sdd_check.cmd_gate_ship(
                argparse.Namespace(tech_spec_path=tech, stories_path=stories, ids=None)
            )
            self.assertEqual(rc, 0)
        finally:
            os.remove(tech)
            os.remove(stories)

    def test_gate_blocks_when_a_story_is_not_passing(self):
        import argparse

        tech = write_tmp(self.TECH_SPEC)
        stories = write_tmp(self.STORIES_ONE_NOT_PASSING)
        try:
            rc = sdd_check.cmd_gate_ship(
                argparse.Namespace(tech_spec_path=tech, stories_path=stories, ids=None)
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(tech)
            os.remove(stories)

    def test_gate_blocks_whole_feature_ship_when_an_ac_has_no_story(self):
        import argparse

        tech = write_tmp(self.TECH_SPEC)
        stories = write_tmp(self.STORIES_MISSING_AC_COVERAGE)
        try:
            rc = sdd_check.cmd_gate_ship(
                argparse.Namespace(tech_spec_path=tech, stories_path=stories, ids=None)
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(tech)
            os.remove(stories)

    def test_partial_ship_with_ids_skips_whole_feature_ac_closure(self):
        import argparse

        # AC-2 has no story at all, but we only target US-001 (AC-1) —
        # a partial ship shouldn't be blocked by an AC outside its scope.
        tech = write_tmp(self.TECH_SPEC)
        stories = write_tmp(self.STORIES_MISSING_AC_COVERAGE)
        try:
            rc = sdd_check.cmd_gate_ship(
                argparse.Namespace(
                    tech_spec_path=tech, stories_path=stories, ids=["US-001"]
                )
            )
            self.assertEqual(rc, 0)
        finally:
            os.remove(tech)
            os.remove(stories)

    def test_gate_blocks_on_unknown_targeted_id(self):
        import argparse

        tech = write_tmp(self.TECH_SPEC)
        stories = write_tmp(self.STORIES_ALL_PASSING)
        try:
            rc = sdd_check.cmd_gate_ship(
                argparse.Namespace(
                    tech_spec_path=tech, stories_path=stories, ids=["US-999"]
                )
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(tech)
            os.remove(stories)

    def test_gate_blocks_on_missing_tech_spec(self):
        import argparse

        stories = write_tmp(self.STORIES_ALL_PASSING)
        try:
            rc = sdd_check.cmd_gate_ship(
                argparse.Namespace(
                    tech_spec_path="/no/such/tech-spec.md",
                    stories_path=stories,
                    ids=None,
                )
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(stories)

    def test_gate_blocks_on_missing_stories_file(self):
        import argparse

        tech = write_tmp(self.TECH_SPEC)
        try:
            rc = sdd_check.cmd_gate_ship(
                argparse.Namespace(
                    tech_spec_path=tech,
                    stories_path="/no/such/stories.md",
                    ids=None,
                )
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(tech)

    def test_gate_blocks_on_tech_spec_with_no_ac_bullets(self):
        import argparse

        tech = write_tmp("## Acceptance criteria\n<nothing yet>\n")
        stories = write_tmp(self.STORIES_ALL_PASSING)
        try:
            rc = sdd_check.cmd_gate_ship(
                argparse.Namespace(tech_spec_path=tech, stories_path=stories, ids=None)
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(tech)
            os.remove(stories)


class TransitionValidationTests(unittest.TestCase):
    def test_legal_forward_steps_allowed(self):
        self.assertIsNone(
            sdd_check._validate_transition("Ready for Implementation", "Implemented")
        )
        self.assertIsNone(sdd_check._validate_transition("Implemented", "Passing"))

    def test_skipping_a_phase_is_blocked(self):
        self.assertIsNotNone(
            sdd_check._validate_transition("Ready for Implementation", "Passing")
        )

    def test_going_backward_is_blocked(self):
        self.assertIsNotNone(
            sdd_check._validate_transition("Implemented", "Ready for Implementation")
        )

    def test_failing_reachable_only_from_implemented_or_passing(self):
        self.assertIsNone(
            sdd_check._validate_transition("Implemented", "Failing: assertion error")
        )
        self.assertIsNone(
            sdd_check._validate_transition("Passing", "Failing: regression")
        )
        self.assertIsNotNone(
            sdd_check._validate_transition("Ready for Implementation", "Failing: n/a")
        )

    def test_recovering_from_failing(self):
        self.assertIsNone(
            sdd_check._validate_transition("Failing: timeout", "Implemented")
        )
        self.assertIsNone(sdd_check._validate_transition("Failing: timeout", "Passing"))
        self.assertIsNotNone(
            sdd_check._validate_transition("Failing: timeout", "Ready for Implementation")
        )

    def test_same_status_is_idempotent_noop(self):
        self.assertIsNone(sdd_check._validate_transition("Passing", "Passing"))
        self.assertIsNone(
            sdd_check._validate_transition("Failing: x", "Failing: x")
        )

    def test_unrecognized_status_is_blocked(self):
        self.assertIsNotNone(
            sdd_check._validate_transition("Ready for Implementation", "Done")
        )


class SetStatusCliTests(unittest.TestCase):
    def test_set_status_rewrites_only_target_story(self):
        import argparse

        text = (
            "## US-001: First\n"
            "- **Status**: Ready for Implementation\n"
            "- **Story**: As a user, I want X.\n"
            "## US-002: Second\n"
            "- **Status**: Ready for Implementation\n"
        )
        path = write_tmp(text)
        try:
            rc = sdd_check.cmd_set_status(
                argparse.Namespace(
                    stories_path=path,
                    story_id="US-001",
                    new_status="Implemented",
                )
            )
            self.assertEqual(rc, 0)
            with open(path) as f:
                out = f.read()
            self.assertIn("US-001: First\n- **Status**: Implemented", out)
            self.assertIn(
                "US-002: Second\n- **Status**: Ready for Implementation", out
            )
        finally:
            os.remove(path)

    def test_set_status_blocks_illegal_transition_and_does_not_write(self):
        import argparse

        text = "## US-001: First\n- **Status**: Ready for Implementation\n"
        path = write_tmp(text)
        try:
            rc = sdd_check.cmd_set_status(
                argparse.Namespace(
                    stories_path=path, story_id="US-001", new_status="Passing"
                )
            )
            self.assertEqual(rc, 1)
            with open(path) as f:
                out = f.read()
            self.assertIn("**Status**: Ready for Implementation", out)
        finally:
            os.remove(path)

    def test_set_status_unknown_story_id_blocks(self):
        import argparse

        text = "## US-001: First\n- **Status**: Ready for Implementation\n"
        path = write_tmp(text)
        try:
            rc = sdd_check.cmd_set_status(
                argparse.Namespace(
                    stories_path=path,
                    story_id="US-404",
                    new_status="Implemented",
                )
            )
            self.assertEqual(rc, 1)
        finally:
            os.remove(path)

    def test_set_status_missing_file_blocks_cleanly(self):
        import argparse

        rc = sdd_check.cmd_set_status(
            argparse.Namespace(
                stories_path="/no/such/stories.md",
                story_id="US-001",
                new_status="Implemented",
            )
        )
        self.assertEqual(rc, 1)


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, SDD_CHECK_PATH, *args],
        capture_output=True,
        text=True,
    )


class CliSubprocessTests(unittest.TestCase):
    """Every test above calls cmd_* directly with a hand-built Namespace,
    which never exercises argparse itself — a wrong dest/flag/nargs in
    main()'s subparsers would pass every one of those tests and still
    break the real CLI. These invoke the script as a real subprocess
    through its actual argv/argparse wiring."""

    def test_slug_cli(self):
        result = run_cli("slug", "Cancel an Order!! (v2)")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "cancel-an-order-v2")

    def test_gate_clarifications_cli_blocks(self):
        path = write_tmp("- **REQ-001**: NEEDS CLARIFICATION: eh?\n")
        try:
            result = run_cli("gate-clarifications", path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("REQ-001", result.stdout)
        finally:
            os.remove(path)

    def test_gate_tests_cli_passes(self):
        path = write_tmp(
            "- **AC-1** [REQ-001]: Given X, when Y, then Z.\n"
            "  - Test: `tests/Foo.cs::Does_X` — red\n"
        )
        try:
            result = run_cli("gate-tests", path, "--acs", "AC-1")
            self.assertEqual(result.returncode, 0)
        finally:
            os.remove(path)

    def test_gate_stories_cli_blocks_on_unknown_id(self):
        path = write_tmp("## US-001: First\n- **Status**: Ready for Implementation\n")
        try:
            result = run_cli("gate-stories", path, "--ids", "US-999")
            self.assertEqual(result.returncode, 1)
        finally:
            os.remove(path)

    def test_set_status_cli_rewrites_file(self):
        path = write_tmp("## US-001: First\n- **Status**: Ready for Implementation\n")
        try:
            result = run_cli("set-status", path, "US-001", "Implemented")
            self.assertEqual(result.returncode, 0)
            with open(path) as f:
                self.assertIn("**Status**: Implemented", f.read())
        finally:
            os.remove(path)

    def test_missing_subcommand_is_a_usage_error(self):
        result = run_cli()
        self.assertNotEqual(result.returncode, 0)

    def test_gate_coverage_cli_passes(self):
        spec = write_tmp("- **REQ-001**: Users can log in.\n")
        tech = write_tmp(
            "- **TS-001** [REQ-001]: Login endpoint.\n"
            "- **AC-1** [REQ-001/TS-001]: Given X, when Y, then Z.\n"
        )
        try:
            result = run_cli("gate-coverage", spec, tech)
            self.assertEqual(result.returncode, 0)
        finally:
            os.remove(spec)
            os.remove(tech)

    def test_gate_clarifications_cli_missing_file_has_no_traceback(self):
        result = run_cli("gate-clarifications", "/no/such/spec.md")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")
        self.assertIn("BLOCKED", result.stdout)

    def test_gate_stories_cli_missing_file_has_no_traceback(self):
        result = run_cli("gate-stories", "/no/such/stories.md")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")
        self.assertIn("BLOCKED", result.stdout)

    def test_gate_ship_cli_passes_when_all_passing_and_covered(self):
        tech = write_tmp("- **AC-1** [REQ-001/TS-001]: Given X, when Y, then Z.\n")
        stories = write_tmp(
            "## US-001: First\n"
            "- **Covers**: AC-1 (REQ-001/TS-001)\n"
            "- **Status**: Passing\n"
        )
        try:
            result = run_cli("gate-ship", tech, stories)
            self.assertEqual(result.returncode, 0)
            self.assertIn("ready to ship", result.stdout)
        finally:
            os.remove(tech)
            os.remove(stories)

    def test_gate_ship_cli_blocks_on_story_not_passing(self):
        tech = write_tmp("- **AC-1** [REQ-001/TS-001]: Given X, when Y, then Z.\n")
        stories = write_tmp(
            "## US-001: First\n"
            "- **Covers**: AC-1 (REQ-001/TS-001)\n"
            "- **Status**: Implemented\n"
        )
        try:
            result = run_cli("gate-ship", tech, stories)
            self.assertEqual(result.returncode, 1)
            self.assertIn("not Passing", result.stdout)
        finally:
            os.remove(tech)
            os.remove(stories)

    def test_gate_ship_cli_missing_file_has_no_traceback(self):
        result = run_cli("gate-ship", "/no/such/tech-spec.md", "/no/such/stories.md")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")
        self.assertIn("BLOCKED", result.stdout)

    def test_set_status_cli_missing_file_has_no_traceback(self):
        result = run_cli("set-status", "/no/such/stories.md", "US-001", "Implemented")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")
        self.assertIn("BLOCKED", result.stdout)


if __name__ == "__main__":
    unittest.main()
