"""Offline fixtures for the search index verdict in tasks/rlm_rebuild_search_index.py.

The cases that matter are the two the index status field gets wrong or can't see:
- a build that completed while ``lastBuildStatus`` still says IN_PROGRESS (measured on a
  264 org);
- a completed build that predates the org, which is what a Trialforce-spun org inherits
  from its template.
Stdlib only. Run with: python tests/test_search_index_readiness.py
"""
import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("_rebuild_search_index", REPO / "tasks" / "rlm_rebuild_search_index.py")
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

ORG_CREATED = "2026-10-16T03:20:32.000+0000"


def snapshots(*logs, status="ACTIVE", last_build="IN_PROGRESS"):
    """A snapshots response with one snapshot holding one index with these logs."""
    return {"snapshots": [{
        "activationStatus": status,
        "snapshotIndexes": [{"lastBuildStatus": last_build, "indexLogs": list(logs)}],
    }]}


def log(status, completed, build="FULL", message=None):
    return {"indexBuildStatus": status, "completionTime": completed, "indexBuildType": build, "message": message}


class IndexReadiness(unittest.TestCase):

    def verdict(self, response, created=ORG_CREATED):
        return mod.index_readiness(response, created)[0]

    def test_completed_after_creation_is_ready_whatever_last_build_status_says(self):
        # The live shape: one completed full build, status field still IN_PROGRESS.
        response = snapshots(log("COMPLETED", "2026-10-27T22:18:30.000Z"), last_build="IN_PROGRESS")
        self.assertEqual(self.verdict(response), mod.READY)

    def test_completed_before_creation_is_not_built_here(self):
        response = snapshots(log("COMPLETED", "2026-09-01T10:00:00.000Z"), last_build="COMPLETED")
        self.assertEqual(self.verdict(response), mod.NOT_BUILT_HERE)

    def test_inherited_build_plus_one_built_here_is_ready(self):
        response = snapshots(log("COMPLETED", "2026-09-01T10:00:00.000Z"),
                             log("COMPLETED", "2026-10-20T10:00:00.000Z"))
        self.assertEqual(self.verdict(response), mod.READY)

    def test_running_with_no_completed_build_here_is_building(self):
        response = snapshots(log("COMPLETED", "2026-09-01T10:00:00.000Z"), log("IN_PROGRESS", None))
        self.assertEqual(self.verdict(response), mod.BUILDING)

    def test_latest_failure_with_nothing_built_here_is_failed(self):
        response = snapshots(log("COMPLETED", "2026-09-01T10:00:00.000Z"),
                             log("FAILED", "2026-10-20T10:00:00.000Z", message="Catalog unavailable"))
        verdict, detail = mod.index_readiness(response, ORG_CREATED)
        self.assertEqual(verdict, mod.FAILED)
        self.assertIn("Catalog unavailable", detail)

    def test_no_active_snapshot_is_no_index(self):
        response = snapshots(log("COMPLETED", "2026-10-27T22:18:30.000Z"), status="EXPIRED")
        self.assertEqual(self.verdict(response), mod.NO_INDEX)
        self.assertEqual(self.verdict({"snapshots": []}), mod.NO_INDEX)
        self.assertEqual(self.verdict(None), mod.NO_INDEX)

    def test_both_timestamp_offsets_parse_to_the_same_instant(self):
        # The snapshots API writes Z; Organization.CreatedDate writes +0000.
        self.assertEqual(mod._parse_time("2026-10-16T03:20:32.000Z"), mod._parse_time(ORG_CREATED))

    def test_a_build_finishing_the_same_instant_as_creation_is_not_after_it(self):
        response = snapshots(log("COMPLETED", "2026-10-16T03:20:32.000Z"))
        self.assertEqual(self.verdict(response), mod.NOT_BUILT_HERE)

    def test_rebuild_in_flight_on_a_built_org_stays_ready(self):
        # Measured shape mid-rebuild: the active snapshot's new log is IN_PROGRESS, no time.
        response = snapshots(log("IN_PROGRESS", None), log("COMPLETED", "2026-10-27T22:18:30.000Z"))
        self.assertEqual(self.verdict(response), mod.READY)

    def test_ready_mentions_a_later_failed_build(self):
        response = snapshots(log("COMPLETED", "2026-10-20T10:00:00.000Z"),
                             log("FAILED", "2026-10-25T10:00:00.000Z", message="Catalog unavailable"))
        verdict, detail = mod.index_readiness(response, ORG_CREATED)
        self.assertEqual(verdict, mod.READY)
        self.assertIn("Catalog unavailable", detail)

    def test_a_build_running_on_a_snapshot_not_yet_active_is_building(self):
        response = {"snapshots": [
            {"activationStatus": "ACTIVE", "snapshotIndexes": [{"indexLogs": [log("COMPLETED", "2026-09-01T10:00:00.000Z")]}]},
            {"activationStatus": "PENDING", "snapshotIndexes": [{"indexLogs": [log("IN_PROGRESS", None)]}]},
        ]}
        self.assertEqual(self.verdict(response), mod.BUILDING)
        self.assertEqual(self.verdict({"snapshots": [response["snapshots"][1]]}), mod.BUILDING)

    def test_an_unrecognised_status_is_reported_not_called_failed(self):
        verdict, detail = mod.index_readiness(snapshots(log("QUEUED", None)), ORG_CREATED)
        self.assertEqual(verdict, mod.BUILDING)
        self.assertIn("QUEUED", detail)

    def test_an_unreadable_creation_date_is_an_error_not_a_pass(self):
        # Treating it as "any completed build counts" would call an inherited build Ready.
        response = snapshots(log("COMPLETED", "2026-09-01T10:00:00.000Z"))
        for created in (None, "", "not a date", 12345):
            with self.subTest(created=created):
                with self.assertRaises(ValueError):
                    mod.index_readiness(response, created)

    def test_a_stale_in_progress_log_on_an_expired_snapshot_does_not_block_the_verdict(self):
        response = {"snapshots": [
            {"activationStatus": "ACTIVE", "snapshotIndexes": [{"indexLogs": [log("COMPLETED", "2026-09-01T10:00:00.000Z")]}]},
            {"activationStatus": "EXPIRED", "snapshotIndexes": [{"indexLogs": [log("IN_PROGRESS", None)]}]},
        ]}
        self.assertEqual(self.verdict(response), mod.NOT_BUILT_HERE)

    def test_a_dated_unrecognised_status_is_terminal_not_building(self):
        verdict, detail = mod.index_readiness(snapshots(log("CANCELLED", "2026-10-20T10:00:00.000Z")), ORG_CREATED)
        self.assertEqual(verdict, mod.FAILED)
        self.assertIn("CANCELLED", detail)

    def test_an_unparseable_time_is_undated_not_a_crash(self):
        self.assertIsNone(mod._parse_time("yesterday"))
        self.assertEqual(self.verdict(snapshots(log("IN_PROGRESS", "yesterday"))), mod.BUILDING)


class _Response:
    def __init__(self, status, body, text=None):
        self.status_code = status
        self._body = body
        self.text = text if text is not None else str(body)

    def json(self):
        if isinstance(self._body, Exception):
            raise self._body
        return self._body


class CheckSearchIndexReadinessTask(unittest.TestCase):
    """The task wrapper, with `requests` replaced: HTTP errors, bad bodies and strict."""

    def run_task(self, snapshots_response, org_response, strict=False):
        import sys
        import types

        fake = types.ModuleType("requests")
        fake.get = lambda url, **kw: snapshots_response if url.endswith("/snapshots") else org_response
        task = object.__new__(mod.CheckSearchIndexReadiness)
        task.options = {"strict": strict}
        task.project_config = types.SimpleNamespace(project__package__api_version="68.0")
        task.org_config = types.SimpleNamespace(instance_url="https://example.my.salesforce.com", access_token="t")
        task.logger = types.SimpleNamespace(info=lambda *a: None, warning=lambda *a: None)
        saved = sys.modules.get("requests")
        sys.modules["requests"] = fake
        try:
            return mod.CheckSearchIndexReadiness._run_task(task)
        finally:
            if saved is None:
                del sys.modules["requests"]
            else:
                sys.modules["requests"] = saved

    ORG = _Response(200, {"records": [{"CreatedDate": ORG_CREATED}]})

    def test_ready_returns_the_verdict(self):
        result = self.run_task(_Response(200, snapshots(log("COMPLETED", "2026-10-27T22:18:30.000Z"))), self.ORG, strict=True)
        self.assertEqual(result["verdict"], mod.READY)

    def test_strict_fails_when_not_ready_and_reports_otherwise(self):
        inherited = _Response(200, snapshots(log("COMPLETED", "2026-09-01T10:00:00.000Z")))
        self.assertEqual(self.run_task(inherited, self.ORG)["verdict"], mod.NOT_BUILT_HERE)
        with self.assertRaisesRegex(mod.CumulusCIException, "not ready"):
            self.run_task(inherited, self.ORG, strict=True)

    def test_http_error_non_json_and_bad_shapes_raise_a_task_error(self):
        # The message is asserted, not only the type: offline, CumulusCIException is plain
        # Exception, so a bare AttributeError would satisfy assertRaises.
        for snaps, org, message in (
            (_Response(500, {}, "server error"), self.ORG, "Could not read the search index snapshots"),
            (_Response(200, ValueError("not json"), "<html>"), self.ORG, "was not JSON"),
            (_Response(200, ["not", "a", "dict"]), self.ORG, "Unexpected search index snapshots response"),
            (_Response(200, {"snapshots": []}), _Response(200, {"records": []}), "Could not read Organization.CreatedDate"),
            (_Response(200, {"snapshots": []}), _Response(200, {"records": [{"CreatedDate": None}]}), "CreatedDate is unreadable"),
            (_Response(200, {"snapshots": []}), _Response(200, {"records": [{"CreatedDate": "soon"}]}), "CreatedDate is unreadable"),
        ):
            with self.subTest(message=message):
                with self.assertRaisesRegex(mod.CumulusCIException, message):
                    self.run_task(snaps, org)


if __name__ == "__main__":
    unittest.main()
