"""Unit tests for scripts/sdd_check.py — the gate script every klk- command
trusts. Stdlib unittest only, no deps, matching the script's own constraint.

Run: python3 -m unittest discover -s scripts/tests
"""
import importlib.util
import os
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


if __name__ == "__main__":
    unittest.main()
