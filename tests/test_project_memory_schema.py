#!/usr/bin/env python3
"""`.agents/context/project-memory.json` conforms to `.agents/schemas/project-memory.schema.json`.

Nothing else validates the file, so without this the schema documents the format but does not
enforce it. A stdlib validator rather than `jsonschema`: in pr_gate a missing dependency fails the
run, and every workstation, the Docker image and CI would need the package to guard one small file.

⚠ The validator implements only the keywords (and keyword values) the schema uses, and it FAILS on
anything else, wherever it appears. A later schema edit that adds a rule (`maxItems`, `oneOf`,
`"format": "uri"`, a type list) must extend the validator, not be silently ignored by it.

Two deliberate departures from a default 2020-12 validator, so `jsonschema` may disagree:
- `format` is ASSERTED (2020-12 treats it as an annotation unless the format-assertion vocabulary
  is enabled). A `date-time` field holding "yesterday" is exactly the bad edit this exists to catch.
- date-time is RFC 3339 minus leap seconds (`:60` fails).

Run with: python tests/test_project_memory_schema.py
"""
import copy
import datetime
import json
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO / ".agents" / "schemas" / "project-memory.schema.json"
MEMORY_PATH = REPO / ".agents" / "context" / "project-memory.json"

# Keywords with no effect on validity. `$defs` holds subschemas, reached only through `$ref`.
ANNOTATIONS = {"$schema", "$id", "title", "description", "$defs"}
ASSERTIONS = {"type", "required", "additionalProperties", "properties", "pattern", "enum",
              "minLength", "minItems", "items", "$ref", "format"}

# Only the types the schema uses. `integer`/`number` are left out on purpose: JSON Schema counts
# 1.0 as an integer and Python does not, so adding them means deciding that, not copying a lambda.
TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
}
FORMATS = {"date", "date-time"}

# RFC 3339 date-time, parsed by hand: fromisoformat's accepted forms differ across 3.9 / 3.11+
# (a trailing `Z`, fraction lengths, a space separator), and the verdict must not.
_DATE_TIME = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})[Tt](\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:[Zz]|[+-](\d{2}):(\d{2}))",
    re.ASCII)
_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})", re.ASCII)


def _valid_format(fmt, value):
    m = (_DATE_TIME if fmt == "date-time" else _DATE).fullmatch(value)
    if not m:
        return False
    y, mo, d = (int(g) for g in m.groups()[:3])
    try:
        datetime.date(y, mo, d)
    except ValueError:
        return False
    if fmt == "date":
        return True
    hh, mm, ss = (int(g) for g in m.groups()[3:6])
    off_h, off_m = m.group(7), m.group(8)
    return (hh < 24 and mm < 60 and ss < 60
            and (off_h is None or (int(off_h) < 24 and int(off_m) < 60)))


def _compile_pattern(pattern):
    """Compile an ECMA-262 pattern with ECMA semantics for the constructs this schema uses.

    Python's `$` also matches before a trailing newline and ECMA's does not, so "1.0.0\n" would pass
    `^...$` here and fail everywhere else. A trailing `$` becomes `\\Z`; a `$` anywhere else is
    refused. re.ASCII makes `\\d`/`\\w` ASCII, as in ECMA without the `u` flag.
    """
    # A pattern ending in a backslash and `$` is a literal `$` (`\$`) or, after an escaped backslash
    # (`\\$`), an anchor. Telling them apart means counting backslashes, and no pattern here needs it.
    if pattern.endswith("\\$"):
        raise ValueError(f"pattern {pattern!r}: a final `\\$` is not implemented")
    body = pattern
    if body.endswith("$"):
        body = body[:-1] + r"\Z"
    if re.search(r"(?<!\\)\$", body):
        raise ValueError(f"pattern {pattern!r}: `$` other than as the final anchor is not implemented")
    return re.compile(body, re.ASCII)


def _resolve(ref, root):
    node = root
    for part in ref[2:].split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


def check_schema(schema, root=None, where="#"):
    """Raise on any keyword or keyword value the validator does not implement, anywhere.

    Static, not done during validation: validation reaches only the subschemas the instance
    exercises, so an empty array's `items` or an absent optional property would go unchecked.
    After this passes, validate() has nothing left to refuse.
    """
    root = schema if root is None else root
    if not isinstance(schema, dict):
        raise ValueError(f"{where}: boolean or non-object schemas are not implemented")
    unknown = set(schema) - ANNOTATIONS - ASSERTIONS
    if unknown:
        raise ValueError(f"{where}: schema uses unsupported keyword(s) {sorted(unknown)}")
    if "$ref" in schema:
        ref = schema["$ref"]
        # 2020-12 lets $ref sit beside other keywords; this schema never does, and supporting it
        # would mean deciding how the two combine. Refuse rather than guess.
        if set(schema) - ANNOTATIONS != {"$ref"}:
            raise ValueError(f"{where}: $ref alongside other assertions is not implemented")
        # Only to a top-level $defs entry: each is checked below as a schema, and a pointer elsewhere
        # (`#/required`, or `#/$defs/x/properties`, a map of schemas) is not a schema at all.
        if not isinstance(ref, str) or not re.fullmatch(r"#/\$defs/[^/]+", ref):
            raise ValueError(f"{where}: $ref {ref!r}: only local `#/$defs/...` pointers are implemented")
        try:
            target = _resolve(ref, root)
        except (KeyError, TypeError):
            raise ValueError(f"{where}: $ref {ref!r} does not resolve") from None
        if not isinstance(target, dict):
            raise ValueError(f"{where}: $ref {ref!r} does not point at a schema")
    if "type" in schema and (not isinstance(schema["type"], str) or schema["type"] not in TYPES):
        raise ValueError(f"{where}: unsupported type {schema['type']!r}")
    if "format" in schema and schema["format"] not in FORMATS:
        raise ValueError(f"{where}: unsupported format {schema['format']!r}")
    if "additionalProperties" in schema and not isinstance(schema["additionalProperties"], bool):
        raise ValueError(f"{where}: additionalProperties as a schema is not implemented")
    for key in ("required", "enum"):
        if key in schema and not isinstance(schema[key], list):
            raise ValueError(f"{where}: {key} must be a list")
    # Python `in` equates True with 1; JSON Schema does not. A string type rules that out.
    if "enum" in schema and schema.get("type") != "string":
        raise ValueError(f"{where}: enum without `type: string` is not implemented")
    for key in ("minLength", "minItems"):
        if key in schema and (type(schema[key]) is not int or schema[key] < 0):
            raise ValueError(f"{where}: {key} must be a non-negative integer")
    if "pattern" in schema:
        _compile_pattern(schema["pattern"])
    for name, sub in schema.get("properties", {}).items():
        check_schema(sub, root, f"{where}/properties/{name}")
    for name, sub in schema.get("$defs", {}).items():
        check_schema(sub, root, f"{where}/$defs/{name}")
    if "items" in schema:
        check_schema(schema["items"], root, f"{where}/items")


def validate(instance, schema, root=None, path="$"):
    """Return a list of `path: message` errors (empty when valid). Raises on an unsupported schema."""
    if root is None:
        root = schema
        check_schema(schema)
    if "$ref" in schema:
        return validate(instance, _resolve(schema["$ref"], root), root, path)

    errors = []
    if "type" in schema and not TYPES[schema["type"]](instance):
        # Nothing below is meaningful against the wrong type.
        return [f"{path}: expected {schema['type']}, got {type(instance).__name__}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in {schema['enum']}")
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "pattern" in schema and not _compile_pattern(schema["pattern"]).search(instance):
            errors.append(f"{path}: {instance!r} does not match {schema['pattern']!r}")
        if "format" in schema and not _valid_format(schema["format"], instance):
            errors.append(f"{path}: {instance!r} is not a valid {schema['format']}")
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems {schema['minItems']}")
        if "items" in schema:
            for i, item in enumerate(instance):
                errors += validate(item, schema["items"], root, f"{path}[{i}]")
    if isinstance(instance, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required key {key!r}")
        extra = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in props:
                errors += validate(value, props[key], root, f"{path}.{key}")
            elif extra is False:
                errors.append(f"{path}: unexpected key {key!r}")
    return errors


class ProjectMemorySchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.memory = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))

    def errors_after(self, mutate):
        doc = copy.deepcopy(self.memory)
        mutate(doc)
        return validate(doc, self.schema)

    def test_real_file_conforms(self):
        self.assertEqual(validate(self.memory, self.schema), [])

    def test_missing_required_key_fails(self):
        errs = self.errors_after(lambda d: d["repository"].pop("default_branch"))
        self.assertIn("$.repository: missing required key 'default_branch'", errs)

    def test_extra_key_fails(self):
        errs = self.errors_after(lambda d: d["repository"].__setitem__("salesforce_release", "264"))
        self.assertIn("$.repository: unexpected key 'salesforce_release'", errs)

    def test_pattern_mismatch_fails(self):
        errs = self.errors_after(lambda d: d.__setitem__("schema_version", "1.0"))
        self.assertTrue(any(e.startswith("$.schema_version:") and "does not match" in e for e in errs), errs)

    def test_pattern_through_ref_fails(self):
        errs = self.errors_after(lambda d: d["high_risk_safety_constraints"][0].__setitem__("id", "lower-case"))
        self.assertTrue(any(e.startswith("$.high_risk_safety_constraints[0].id:") for e in errs), errs)

    def test_wrong_type_fails(self):
        errs = self.errors_after(lambda d: d.__setitem__("key_directories", {}))
        self.assertEqual(errs, ["$.key_directories: expected array, got dict"])

    def test_bad_enum_fails(self):
        errs = self.errors_after(lambda d: d["repository"].__setitem__("source_format", "mdapi"))
        self.assertTrue(any(e.startswith("$.repository.source_format:") and "not in" in e for e in errs), errs)

    def test_empty_string_fails_min_length(self):
        errs = self.errors_after(lambda d: d["repository"].__setitem__("name", ""))
        self.assertIn("$.repository.name: shorter than minLength 1", errs)

    def test_empty_array_fails_min_items(self):
        errs = self.errors_after(lambda d: d.__setitem__("external_systems", []))
        self.assertIn("$.external_systems: fewer than minItems 1", errs)

    def test_bad_date_time_fails(self):
        for bad in ("2026-10-11", "2026-10-11 04:17:31Z", "2026-13-11T04:17:31Z", "2026-10-11T04:17:31"):
            with self.subTest(bad=bad):
                errs = self.errors_after(lambda d: d.__setitem__("last_updated_utc", bad))
                self.assertTrue(any(e.startswith("$.last_updated_utc:") for e in errs), errs)

    def test_trailing_newline_fails_pattern(self):
        # Python's `$` matches before a final "\n"; ECMA's does not, so this must fail here too.
        for mutate in (lambda d: d.__setitem__("schema_version", "1.0.0\n"),
                       lambda d: d["high_risk_safety_constraints"][0].__setitem__("id", "SAFE-UX-001\n")):
            with self.subTest():
                self.assertTrue(any("does not match" in e for e in self.errors_after(mutate)))

    def test_rfc3339_forms_pass_on_every_interpreter(self):
        # 3.9's fromisoformat rejects a 1-digit fraction and `Z`; the verdict must not vary by version.
        for good in ("2026-10-11T04:17:31.5Z", "2026-10-11t04:17:31z", "2026-10-11T04:17:31+05:30"):
            with self.subTest(good=good):
                self.assertEqual(self.errors_after(lambda d: d.__setitem__("last_updated_utc", good)), [])

    def test_leap_second_and_bad_offset_fail(self):
        for bad in ("2026-10-11T23:59:60Z", "2026-10-11T04:17:31+24:00", "2026-10-11T04:17:31Z\n"):
            with self.subTest(bad=bad):
                errs = self.errors_after(lambda d: d.__setitem__("last_updated_utc", bad))
                self.assertTrue(any(e.startswith("$.last_updated_utc:") for e in errs), errs)

    def test_bad_date_fails(self):
        errs = self.errors_after(lambda d: d["last_successful_optimization_run"].__setitem__("date", "2026-02-30"))
        self.assertTrue(any(e.startswith("$.last_successful_optimization_run.date:") for e in errs), errs)

    def test_bool_is_not_a_string(self):
        errs = self.errors_after(lambda d: d.__setitem__("$schema", True))
        self.assertEqual(errs, ["$.$schema: expected string, got bool"])

    def test_unsupported_keyword_is_refused(self):
        schema = copy.deepcopy(self.schema)
        schema["properties"]["unresolved_recommendations"]["maxItems"] = 5
        with self.assertRaisesRegex(ValueError, r"unsupported keyword\(s\) \['maxItems'\]"):
            validate(self.memory, schema)

    def test_unsupported_keyword_under_unreached_items_is_refused(self):
        # unresolved_recommendations may be empty, so validation alone would never reach its items.
        schema = copy.deepcopy(self.schema)
        schema["properties"]["unresolved_recommendations"]["items"]["properties"]["id"] = {"oneOf": []}
        with self.assertRaisesRegex(ValueError, "oneOf"):
            validate({"unresolved_recommendations": []}, schema)

    def test_unsupported_values_on_unreached_properties_are_refused(self):
        # Each lands on an optional property the instance does not carry, so only a static check sees it.
        rec = ["properties", "unresolved_recommendations", "items", "properties", "suggested_command"]
        cases = {
            "format": ({"type": "string", "format": "uri"}, "unsupported format"),
            "type list": ({"type": ["string", "null"]}, "unsupported type"),
            "integer type": ({"type": "integer"}, "unsupported type"),
            "additionalProperties schema": ({"type": "object", "additionalProperties": {"type": "string"}},
                                            "additionalProperties as a schema"),
            "remote $ref": ({"$ref": "https://example.invalid/s.json"}, "only local"),
            "$ref outside $defs": ({"$ref": "#/required"}, "only local"),
            "$ref into a $defs entry's properties": ({"$ref": "#/$defs/stableItem/properties"}, "only local"),
            "dangling $ref": ({"$ref": "#/$defs/missing"}, "does not resolve"),
            "$ref with siblings": ({"$ref": "#/$defs/stableId", "minLength": 1}, "alongside"),
            "boolean schema": (True, "boolean or non-object"),
            "untyped enum": ({"enum": [1, True]}, "enum without"),
            "inner $": ({"type": "string", "pattern": "a$|b"}, "final anchor"),
            "escaped final $": ({"type": "string", "pattern": "^x\\\\$"}, "final `\\$`"),
        }
        doc = {"unresolved_recommendations": []}
        for name, (sub, message) in cases.items():
            with self.subTest(name):
                schema = copy.deepcopy(self.schema)
                node = schema
                for part in rec[:-1]:
                    node = node[part]
                node[rec[-1]] = sub
                with self.assertRaisesRegex(ValueError, re.escape(message)):
                    validate(doc, schema)

    def test_unsupported_keyword_in_defs_is_refused(self):
        schema = copy.deepcopy(self.schema)
        schema["$defs"]["stableId"]["maxLength"] = 40
        with self.assertRaisesRegex(ValueError, "maxLength"):
            validate(self.memory, schema)


if __name__ == "__main__":
    sys.exit(0 if unittest.main(exit=False).result.wasSuccessful() else 1)
