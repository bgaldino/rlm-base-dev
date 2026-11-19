#!/usr/bin/env python3
"""
Offline tests for tasks/rlm_configure_search_index.ConfigureSearchIndex.

    python tests/test_rlm_configure_search_index.py
    python -m unittest tests.test_rlm_configure_search_index

Stdlib only. The task imports `requests` inside `_run_task`, so each run swaps a fake
`requests` module into sys.modules that records the GET and PUT and answers from a
queue; no org and no network. CumulusCI is optional: the task is built without its
__init__, and the module's no-CumulusCI fallback is loaded on purpose in one case.

What is asserted
----------------
The PUT body is the task's whole effect on the org, so the merge cases assert it
exactly: additive keeps existing entries (sanitized to the PUT-accepted keys), updates
matched ones and adds new ones; replace sends only the file's entries and reports what
it drops. Around that, option parsing (path resolution, mode precedence and validation,
raise_on_failure), every failure path with its message - asserted by text, because
offline CumulusCIException is plain Exception and any error would satisfy the type -
and the pure helpers that resolve field types and convert 15-character Ids.
"""
import importlib.util
import json
import logging
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tasks import rlm_configure_search_index as mod  # noqa: E402
from tasks.rlm_configure_search_index import ConfigureSearchIndex  # noqa: E402

INSTANCE = "https://example.my.salesforce.com"
TOKEN = "00Dxx0000000001!FAKE"
API = "66.0"
BASE = f"{INSTANCE}/services/data/v{API}/connect/pcm/index/configurations"

METADATA = {
    "objectInfos": [
        {
            "name": "Product2",
            "fields": [
                {"name": "Name", "type": "Standard"},
                {"name": "Family", "type": "Standard"},
                {"name": "RLM_Timeline__c", "type": "Custom", "customFieldId": "00NEc00001Ce1Vr"},
            ],
        },
        {
            "name": "ProductAttributeDefinition",
            "fields": [
                {"name": "Name", "type": "ProductAttributeDefinitionStandard"},
                {"name": "Color", "type": "ProductDynamicAttribute",
                 "attributeDefinitionId": "0tjEc0000000001"},
                {"name": "Custom_Attr__c", "type": "ProductAttributeDefinitionCustom",
                 "customFieldId": "00NEc00001Xy9Ab"},
            ],
        },
    ]
}

EXISTING = [
    {"name": "Name", "type": "Standard", "isSearchable": True, "isFacetable": False,
     "label": "Product Name"},
    {"name": "RLM_Timeline__c", "type": "Custom", "isSearchable": True, "isFacetable": False,
     "attributeFieldId": "00NEc00001Ce1VrMAJ", "label": "Timeline", "dataType": "dynamicenum"},
]


class FakeResponse:
    def __init__(self, status, body=None, text=""):
        self.status_code = status
        self._body = body
        self.text = text

    def json(self):
        if isinstance(self._body, Exception):
            raise self._body
        return self._body


class FakeRequestException(Exception):
    pass


def fake_requests(get=None, put=None):
    """A `requests` stand-in. `get`/`put` are a FakeResponse or an exception to raise."""
    module = types.ModuleType("requests")
    module.RequestException = FakeRequestException
    module.calls = []

    def _answer(method, answer, url, kwargs):
        module.calls.append((method, url, kwargs))
        if isinstance(answer, BaseException):
            raise answer
        if answer is None:
            raise AssertionError(f"unexpected {method} {url}")
        return answer

    module.get = lambda url, **kw: _answer("GET", get, url, kw)
    module.put = lambda url, **kw: _answer("PUT", put, url, kw)
    return module


def get_ok(existing=None, metadata=METADATA):
    return FakeResponse(200, {"indexConfigurations": list(existing or []), "metadata": metadata})


class TaskCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = tmp.name

    def write_config(self, body, rel="datasets/search_index/test.json"):
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(body if isinstance(body, str) else json.dumps(body))
        return rel

    def make_task(self, **options):
        task = ConfigureSearchIndex.__new__(ConfigureSearchIndex)
        task.options = options
        task.logger = logging.getLogger("test_rlm_configure_search_index")
        task.project_config = SimpleNamespace(repo_root=self.repo, project__package__api_version=API)
        task.org_config = SimpleNamespace(instance_url=INSTANCE, access_token=TOKEN)
        task.return_values = {}
        return task

    def run_task(self, requests_mod, **options):
        task = self.make_task(**options)
        with mock.patch.dict(sys.modules, {"requests": requests_mod}):
            with self.assertLogs("test_rlm_configure_search_index", level="INFO") as logs:
                result = task._run_task()
        return task, result, "\n".join(logs.output)

    def assert_fails(self, requests_mod, message, **options):
        """Default raise_on_failure: raises with the message. False: warns, returns zeros."""
        task = self.make_task(**options)
        with mock.patch.dict(sys.modules, {"requests": requests_mod}):
            with self.assertRaisesRegex(mod.CumulusCIException,
                                        "PCM index configuration failed: " + message):
                task._run_task()
        calls_when_raising = list(requests_mod.calls)
        requests_mod.calls.clear()
        _, result, logs = self.run_task(requests_mod, raise_on_failure="False", **options)
        self.assertEqual(result, {"added": [], "updated": [], "removed": [], "total_configs": 0})
        self.assertRegex(logs, "WARNING.*PCM index configuration failed: " + message)
        self.assertIn("-- continuing.", logs)
        self.assertEqual(requests_mod.calls, calls_when_raising,
                         "raise_on_failure must not change what reaches the org")
        return calls_when_raising


class ClassContract(unittest.TestCase):
    def test_options(self):
        self.assertEqual(set(ConfigureSearchIndex.task_options), {"path", "mode", "raise_on_failure"})
        self.assertTrue(ConfigureSearchIndex.task_options["path"]["required"])
        self.assertFalse(ConfigureSearchIndex.task_options["mode"]["required"])
        self.assertFalse(ConfigureSearchIndex.task_options["raise_on_failure"]["required"])

    def test_module_imports_without_cumulusci(self):
        blocked = {k: None for k in list(sys.modules) if k == "cumulusci" or k.startswith("cumulusci.")}
        blocked["cumulusci"] = None
        spec = importlib.util.spec_from_file_location(
            "_configure_search_index_no_cci", REPO_ROOT / "tasks" / "rlm_configure_search_index.py"
        )
        fallback = importlib.util.module_from_spec(spec)
        with mock.patch.dict(sys.modules, blocked):
            spec.loader.exec_module(fallback)
        self.assertIs(fallback.BaseSalesforceApiTask, object)
        self.assertIs(fallback.CumulusCIException, Exception)
        for value in (True, "True", "true", " TRUE ", "1", 1, "yes"):
            with self.subTest(value=value):
                self.assertIs(fallback.process_bool_arg(value), True)
        for value in (False, "False", "false", "0", 0, "no", "", None):
            with self.subTest(value=value):
                self.assertIs(fallback.process_bool_arg(value), False)


class ConfigLoading(TaskCase):
    def test_relative_path_resolves_against_repo_root(self):
        rel = self.write_config({"indexConfigurations": [{"name": "Family"}]})
        req = fake_requests(get=get_ok(), put=FakeResponse(200))
        _, _, logs = self.run_task(req, path=rel)
        self.assertIn("Loaded 1 field(s) from test.json (mode=additive)", logs)

    def test_absolute_path_is_used_as_is(self):
        rel = self.write_config({"indexConfigurations": [{"name": "Family"}]}, rel="elsewhere/abs.json")
        req = fake_requests(get=get_ok(), put=FakeResponse(200))
        task = self.make_task(path=os.path.join(self.repo, rel))
        task.project_config.repo_root = "/nonexistent-root"
        with mock.patch.dict(sys.modules, {"requests": req}):
            with self.assertLogs("test_rlm_configure_search_index", level="INFO") as logs:
                task._run_task()
        self.assertIn("Loaded 1 field(s) from abs.json", "\n".join(logs.output))

    def test_missing_file(self):
        req = fake_requests()
        calls = self.assert_fails(req, "Configuration file not found: .*nope\\.json", path="nope.json")
        self.assertEqual(calls, [])

    def test_invalid_json(self):
        rel = self.write_config("{not json")
        calls = self.assert_fails(fake_requests(), "Invalid JSON in .*test\\.json", path=rel)
        self.assertEqual(calls, [])

    def test_index_configurations_must_be_a_list(self):
        rel = self.write_config({"indexConfigurations": {"name": "Family"}})
        calls = self.assert_fails(fake_requests(), "'indexConfigurations' must be an array, got dict",
                                  path=rel)
        self.assertEqual(calls, [])

    def test_empty_or_absent_list_is_a_no_op(self):
        for body in ({"indexConfigurations": []}, {}, {"indexConfigurations": None}):
            with self.subTest(body=body):
                rel = self.write_config(body)
                req = fake_requests()
                _, result, logs = self.run_task(req, path=rel)
                self.assertEqual(result, {"added": [], "updated": [], "removed": [], "total_configs": 0})
                self.assertIn("nothing to do", logs)
                self.assertEqual(req.calls, [], "no HTTP call for an empty config")

    def test_empty_list_short_circuits_before_mode_validation(self):
        # Documents current order: an empty list returns before the mode is checked, so a
        # bad mode next to an empty list is not reported, and replace with an empty list
        # cannot be used to clear the index.
        rel = self.write_config({"mode": "bogus", "indexConfigurations": []})
        _, result, _ = self.run_task(fake_requests(), path=rel)
        self.assertEqual(result["total_configs"], 0)


class ModeOption(TaskCase):
    def mode_logged(self, config_mode=None, option_mode=None):
        body = {"indexConfigurations": [{"name": "Family"}]}
        if config_mode is not None:
            body["mode"] = config_mode
        rel = self.write_config(body)
        req = fake_requests(get=get_ok(EXISTING), put=FakeResponse(200))
        options = {"path": rel}
        if option_mode is not None:
            options["mode"] = option_mode
        _, _, logs = self.run_task(req, **options)
        return logs

    def test_default_is_additive(self):
        self.assertIn("(mode=additive)", self.mode_logged())

    def test_config_file_mode_is_used_when_no_option(self):
        self.assertIn("(mode=replace)", self.mode_logged(config_mode="replace"))

    def test_option_overrides_config_file_and_is_case_insensitive(self):
        self.assertIn("(mode=replace)", self.mode_logged(config_mode="additive", option_mode="REPLACE"))
        self.assertIn("(mode=additive)", self.mode_logged(config_mode="replace", option_mode="Additive"))

    def test_invalid_mode(self):
        rel = self.write_config({"indexConfigurations": [{"name": "Family"}]})
        calls = self.assert_fails(fake_requests(), "Invalid mode 'merge'. Must be 'additive' or 'replace'.",
                                  path=rel, mode="merge")
        self.assertEqual(calls, [])


class HttpAndResolution(TaskCase):
    def config(self, entries):
        return self.write_config({"indexConfigurations": entries})

    def test_get_request_shape(self):
        rel = self.config([{"name": "Family"}])
        req = fake_requests(get=get_ok(), put=FakeResponse(204))
        self.run_task(req, path=rel)
        method, url, kwargs = req.calls[0]
        self.assertEqual(method, "GET")
        self.assertEqual(url, BASE + "?includeMetadata=true")
        self.assertEqual(kwargs["headers"], {
            "Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
        self.assertEqual(kwargs["timeout"], 60)

    def test_get_network_error(self):
        rel = self.config([{"name": "Family"}])
        req = fake_requests(get=FakeRequestException("connection reset"))
        calls = self.assert_fails(req, "GET request failed: connection reset", path=rel)
        self.assertEqual([c[0] for c in calls], ["GET"])

    def test_get_http_error(self):
        rel = self.config([{"name": "Family"}])
        for status in (401, 500, 302):
            with self.subTest(status=status):
                req = fake_requests(get=FakeResponse(status, {}, text="denied"))
                calls = self.assert_fails(req, f"GET HTTP {status} - denied", path=rel)
                self.assertEqual([c[0] for c in calls], ["GET"], "no PUT after a failed GET")

    def test_get_not_json(self):
        rel = self.config([{"name": "Family"}])
        req = fake_requests(get=FakeResponse(200, ValueError("no json")))
        self.assert_fails(req, "GET response was not valid JSON", path=rel)

    def test_entry_must_be_an_object(self):
        rel = self.config([{"name": "Family"}, "Name"])
        calls = self.assert_fails(fake_requests(get=get_ok()),
                                  r"indexConfigurations\[1\] must be an object, got str", path=rel)
        self.assertEqual([c[0] for c in calls], ["GET"])

    def test_entry_must_have_a_name(self):
        rel = self.config([{"isSearchable": True}])
        self.assert_fails(fake_requests(get=get_ok()), "Config entry missing 'name' field.", path=rel)

    def test_unresolvable_field_stops_before_put(self):
        cases = (
            ([{"name": "Nope__c"}], "Field 'Nope__c' not found in index metadata"),
            ([{"name": "Name"}], "Field 'Name' exists in multiple types"),
            ([{"name": "Family", "type": "Custom"}], "Field 'Family' with type 'Custom' not found"),
        )
        for entries, message in cases:
            with self.subTest(message=message):
                rel = self.config(entries)
                calls = self.assert_fails(fake_requests(get=get_ok()), message, path=rel)
                self.assertEqual([c[0] for c in calls], ["GET"])

    def test_missing_metadata_means_nothing_resolves(self):
        rel = self.config([{"name": "Family"}])
        req = fake_requests(get=FakeResponse(200, {"indexConfigurations": None, "metadata": None}))
        self.assert_fails(req, "Field 'Family' not found in index metadata", path=rel)

    def test_put_network_error(self):
        rel = self.config([{"name": "Family"}])
        req = fake_requests(get=get_ok(), put=FakeRequestException("timed out"))
        calls = self.assert_fails(req, "PUT request failed: timed out", path=rel)
        self.assertEqual([c[0] for c in calls], ["GET", "PUT"])

    def test_put_http_error(self):
        rel = self.config([{"name": "Family"}])
        req = fake_requests(get=get_ok(), put=FakeResponse(400, text="INVALID_INPUT"))
        self.assert_fails(req, "PUT HTTP 400 - INVALID_INPUT", path=rel)


class Merge(TaskCase):
    def run_merge(self, entries, existing=EXISTING, **options):
        rel = self.write_config({"indexConfigurations": entries})
        req = fake_requests(get=get_ok(existing), put=FakeResponse(200))
        task, result, logs = self.run_task(req, path=rel, **options)
        method, url, kwargs = req.calls[1]
        self.assertEqual((method, url), ("PUT", BASE))
        self.assertEqual(kwargs["timeout"], 60)
        self.assertEqual(kwargs["headers"]["Authorization"], f"Bearer {TOKEN}")
        return task, result, logs, kwargs["json"]

    def test_additive_keeps_existing_updates_matches_and_adds_new(self):
        entries = [
            {"name": "RLM_Timeline__c", "isFacetable": True, "facetDisplayRank": 2},
            {"name": "Family", "isFacetable": True, "facetDisplayRank": 1},
            {"name": "Color"},
            {"name": "Name", "type": "ProductAttributeDefinitionStandard", "isSearchable": False},
        ]
        task, result, logs, body = self.run_merge(entries)
        self.assertEqual(body, {"indexConfigurations": [
            # existing, untouched, output-only "label" stripped
            {"name": "Name", "type": "Standard", "isSearchable": True, "isFacetable": False},
            # existing, updated in place; label and dataType stripped
            {"name": "RLM_Timeline__c", "type": "Custom", "isSearchable": True, "isFacetable": True,
             "attributeFieldId": "00NEc00001Ce1VrMAJ", "facetDisplayRank": 2},
            {"name": "Family", "type": "Standard", "isSearchable": True, "isFacetable": True,
             "facetDisplayRank": 1},
            {"name": "Color", "type": "ProductDynamicAttribute", "isSearchable": True,
             "isFacetable": False, "attributeDefinitionId": "0tjEc0000000001IAA"},
            {"name": "Name", "type": "ProductAttributeDefinitionStandard", "isSearchable": False,
             "isFacetable": False},
        ]})
        expected = {"added": ["Family", "Color", "Name"], "updated": ["RLM_Timeline__c"],
                    "removed": [], "total_configs": 5}
        self.assertEqual(result, expected)
        self.assertEqual(task.return_values, expected)
        self.assertIn("Updating PCM index configuration: 3 added (Family, Color, Name); "
                      "1 updated (RLM_Timeline__c); 5 total entries.", logs)
        self.assertIn("Run rebuild_search_index", logs)

    def test_additive_rerun_is_idempotent(self):
        entries = [{"name": "Name", "type": "Standard"}]
        _, result, logs, body = self.run_merge(entries)
        self.assertEqual(result["added"], [])
        self.assertEqual(result["updated"], ["Name"])
        self.assertEqual(len(body["indexConfigurations"]), 2)
        self.assertIn("0 added (none); 1 updated (Name)", logs)

    def test_replace_sends_only_the_file_and_reports_removals(self):
        entries = [{"name": "Family", "isFacetable": True}]
        _, result, logs, body = self.run_merge(entries, mode="replace")
        self.assertEqual(body, {"indexConfigurations": [
            {"name": "Family", "type": "Standard", "isSearchable": True, "isFacetable": True},
        ]})
        self.assertEqual(result["added"], ["Family"])
        self.assertEqual(result["updated"], [])
        self.assertEqual(sorted(result["removed"]), ["Custom:RLM_Timeline__c", "Standard:Name"])
        self.assertEqual(result["total_configs"], 1)
        self.assertIn("2 removed (", logs)

    def test_replace_does_not_carry_existing_fields_into_a_kept_entry(self):
        existing = [{"name": "Family", "type": "Standard", "isSearchable": True, "isFacetable": True,
                     "facetDisplayRank": 9}]
        _, result, _, body = self.run_merge([{"name": "Family"}], existing=existing, mode="replace")
        self.assertEqual(body["indexConfigurations"], [
            {"name": "Family", "type": "Standard", "isSearchable": True, "isFacetable": False}])
        self.assertEqual(result["updated"], ["Family"])
        self.assertEqual(result["removed"], [])

    def test_any_2xx_put_is_success(self):
        rel = self.write_config({"indexConfigurations": [{"name": "Family"}]})
        for status in (200, 201, 204):
            with self.subTest(status=status):
                req = fake_requests(get=get_ok(), put=FakeResponse(status))
                _, result, _ = self.run_task(req, path=rel)
                self.assertEqual(result["total_configs"], 1)


class Helpers(unittest.TestCase):
    def test_convert_15_to_18_known_values(self):
        self.assertEqual(mod._convert_15_to_18("00NEc00001Ce1Vr"), "00NEc00001Ce1VrMAJ")
        self.assertEqual(mod._convert_15_to_18("001000000000000"), "001000000000000AAA")
        self.assertEqual(mod._convert_15_to_18("ABCDEABCDEABCDE"), "ABCDEABCDEABCDE555")
        # Bit order within a chunk: first char is bit 0, fifth is bit 4.
        self.assertEqual(mod._convert_15_to_18("Abcdeabcdeabcde"), "AbcdeabcdeabcdeBAA")
        self.assertEqual(mod._convert_15_to_18("abcdEabcdeabcdE"), "abcdEabcdeabcdEQAQ")

    def test_convert_passes_18_through_and_rejects_other_lengths(self):
        self.assertEqual(mod._convert_15_to_18("00NEc00001Ce1VrMAJ"), "00NEc00001Ce1VrMAJ")
        for bad in ("", "00NEc", "00NEc00001Ce1Vr1", "0" * 19):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, f"got {len(bad)}"):
                    mod._convert_15_to_18(bad)

    def test_sanitize_keeps_only_put_keys(self):
        entry = {k: k for k in mod.PUT_ACCEPTED_KEYS}
        entry.update(label="L", dataType="text", extra=1)
        out = mod._sanitize_for_put(entry)
        self.assertEqual(set(out), set(mod.PUT_ACCEPTED_KEYS))
        self.assertIsNot(out, entry)

    def test_build_metadata_index(self):
        meta = {"objectInfos": [
            {"fields": [{"name": "A", "type": "Standard"}, {"name": "B"}, {"type": "Custom"},
                        {"name": "Dup", "type": "Standard"}]},
            {"fields": None},
            {"fields": [{"name": "Dup", "type": "Custom", "customFieldId": "x"}]},
        ]}
        by_name, by_type_name, ambiguous = mod._build_metadata_index(meta)
        self.assertEqual(set(by_name), {"A", "Dup"})
        self.assertEqual(by_name["Dup"]["type"], "Standard", "first occurrence wins in by_name")
        self.assertEqual(set(by_type_name), {("Standard", "A"), ("Standard", "Dup"), ("Custom", "Dup")})
        self.assertEqual(ambiguous, {"Dup"})
        self.assertEqual(mod._build_metadata_index({}), ({}, {}, set()))
        self.assertEqual(mod._build_metadata_index({"objectInfos": None}), ({}, {}, set()))

    def resolve(self, name, desired):
        return mod._resolve_entry(name, desired, *mod._build_metadata_index(METADATA))

    def test_resolve_defaults_and_optional_rank(self):
        self.assertEqual(self.resolve("Family", {}), {
            "name": "Family", "type": "Standard", "isSearchable": True, "isFacetable": False})
        self.assertEqual(
            self.resolve("Family", {"isSearchable": False, "isFacetable": True, "facetDisplayRank": 0}),
            {"name": "Family", "type": "Standard", "isSearchable": False, "isFacetable": True,
             "facetDisplayRank": 0})

    def test_resolve_custom_and_attribute_ids(self):
        self.assertEqual(self.resolve("RLM_Timeline__c", {})["attributeFieldId"], "00NEc00001Ce1VrMAJ")
        self.assertEqual(self.resolve("Custom_Attr__c", {})["attributeFieldId"],
                         mod._convert_15_to_18("00NEc00001Xy9Ab"))
        color = self.resolve("Color", {})
        self.assertEqual(color["attributeDefinitionId"], "0tjEc0000000001IAA")
        self.assertNotIn("attributeFieldId", color)
        self.assertNotIn("attributeFieldId", self.resolve("Family", {}))

    def test_resolve_type_hint_disambiguates(self):
        self.assertEqual(self.resolve("Name", {"type": "Standard"})["type"], "Standard")
        self.assertEqual(self.resolve("Name", {"type": "ProductAttributeDefinitionStandard"})["type"],
                         "ProductAttributeDefinitionStandard")

    def test_resolve_errors(self):
        with self.assertRaisesRegex(ValueError, r"exists in multiple types \(Standard, "
                                                r"ProductAttributeDefinitionStandard\)"):
            self.resolve("Name", {})
        with self.assertRaisesRegex(ValueError, "not found in index metadata"):
            self.resolve("Missing__c", {})
        with self.assertRaisesRegex(ValueError, "with type 'Custom' not found"):
            self.resolve("Family", {"type": "Custom"})
        index = mod._build_metadata_index({"objectInfos": [{"fields": [
            {"name": "NoId__c", "type": "Custom"},
            {"name": "NoAttr", "type": "ProductDynamicAttribute"},
        ]}]})
        with self.assertRaisesRegex(ValueError, "is Custom but has no customFieldId"):
            mod._resolve_entry("NoId__c", {}, *index)
        with self.assertRaisesRegex(ValueError, "ProductDynamicAttribute but has no attributeDefinitionId"):
            mod._resolve_entry("NoAttr", {}, *index)


if __name__ == "__main__":
    unittest.main()
