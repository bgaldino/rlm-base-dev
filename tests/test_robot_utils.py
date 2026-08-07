#!/usr/bin/env python3
"""Offline unit tests for Robot Framework output-directory helpers.

Run from the repository root:

    python tests/test_robot_utils.py

No org, CumulusCI installation, or third-party test dependency is required.
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tasks.robot_utils import (  # noqa: E402
    _sanitize_path_token,
    resolve_robot_output_dir,
)


class SanitizePathTokenTests(unittest.TestCase):
    def test_preserves_safe_characters(self):
        self.assertEqual(
            _sanitize_path_token("task-name_1.2"),
            "task-name_1.2",
        )

    def test_sanitizes_org_username(self):
        self.assertEqual(
            _sanitize_path_token("test-abc+ci@example.com"),
            "test-abc_ci_example.com",
        )

    def test_removes_path_traversal_and_separators(self):
        self.assertEqual(_sanitize_path_token("../../etc\\passwd"), "etc_passwd")

    def test_uses_unknown_for_empty_token(self):
        for value in ("", "..", "___"):
            with self.subTest(value=value):
                self.assertEqual(_sanitize_path_token(value), "unknown")


class ResolveRobotOutputDirTests(unittest.TestCase):
    def test_default_isolates_by_task_and_org(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)

            first = resolve_robot_output_dir(
                repo_root,
                None,
                "robot/rlm-base/results",
                "enable_timeline",
                "first@example.com",
            )
            second_task = resolve_robot_output_dir(
                repo_root,
                None,
                "robot/rlm-base/results",
                "enable_constraints_settings",
                "first@example.com",
            )
            second_org = resolve_robot_output_dir(
                repo_root,
                None,
                "robot/rlm-base/results",
                "enable_timeline",
                "second@example.com",
            )

            self.assertEqual(
                first,
                repo_root
                / "robot/rlm-base/results/enable_timeline/first_example.com",
            )
            self.assertEqual(
                second_task,
                repo_root
                / "robot/rlm-base/results/enable_constraints_settings/first_example.com",
            )
            self.assertEqual(
                second_org,
                repo_root
                / "robot/rlm-base/results/enable_timeline/second_example.com",
            )
            self.assertTrue(all(path.is_dir() for path in (first, second_task, second_org)))

    def test_empty_override_uses_isolated_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)

            result = resolve_robot_output_dir(
                repo_root,
                "",
                "robot/rlm-base/results",
                "enable_timeline",
                "first@example.com",
            )

            self.assertEqual(
                result,
                repo_root
                / "robot/rlm-base/results/enable_timeline/first_example.com",
            )

    def test_relative_override_resolves_from_repo_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)

            result = resolve_robot_output_dir(
                repo_root,
                "custom/robot-results",
                "robot/rlm-base/results",
                "enable_timeline",
                "first@example.com",
            )

            self.assertEqual(result, repo_root / "custom/robot-results")
            self.assertTrue(result.is_dir())

    def test_absolute_override_is_preserved(self):
        with (
            tempfile.TemporaryDirectory() as repo_dir,
            tempfile.TemporaryDirectory() as output_dir,
        ):
            result = resolve_robot_output_dir(
                Path(repo_dir),
                output_dir,
                "robot/rlm-base/results",
                "enable_timeline",
                "first@example.com",
            )

            self.assertEqual(result, Path(output_dir))
            self.assertTrue(result.is_dir())


if __name__ == "__main__":
    unittest.main()
