"""Custom CumulusCI task to configure PCM search index fields.

Reads a declarative JSON configuration from ``datasets/search_index/`` and
applies it to the Product Catalog Management (PCM) search index via the
Connect REST API (``connect/pcm/index/configurations``).

The task is additive — it GETs the current index configuration (with metadata
to auto-resolve field types and IDs), merges in the fields from the config
file, and PUTs the full set back.  Existing configurations are preserved.

Supports all field types: Standard, Custom, ProductDynamicAttribute,
ProductAttributeDefinitionStandard, ProductAttributeDefinitionCustom.
Type and ID resolution is automatic — the config file only needs ``name``
plus the desired ``isSearchable``/``isFacetable`` flags.

Run this AFTER target fields/attributes are deployed to the org.  The
subsequent ``rebuild_search_index`` task triggers the index build that
incorporates the newly-configured fields.
"""
import json
import os

try:
    from cumulusci.tasks.salesforce import BaseSalesforceApiTask
    from cumulusci.core.exceptions import CumulusCIException
    from cumulusci.core.utils import process_bool_arg
except ImportError:  # allow import without cumulusci (e.g. offline doc tooling)
    BaseSalesforceApiTask = object
    CumulusCIException = Exception

    def process_bool_arg(val):  # type: ignore[misc]
        return str(val).strip().lower() in ("true", "1", "yes")


PCM_INDEX_CONFIG_PATH = "connect/pcm/index/configurations"


PUT_ACCEPTED_KEYS = frozenset(
    [
        "attributeDefinitionId",
        "attributeFieldId",
        "facetDisplayRank",
        "isFacetable",
        "isSearchable",
        "name",
        "type",
    ]
)


def _convert_15_to_18(id_15):
    """Convert a 15-character Salesforce ID to its 18-character case-safe form."""
    if len(id_15) == 18:
        return id_15
    if len(id_15) != 15:
        raise ValueError(f"Expected 15-char Salesforce ID, got {len(id_15)}: {id_15}")
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"
    suffix = ""
    for chunk_start in range(0, 15, 5):
        flags = 0
        for i in range(5):
            char = id_15[chunk_start + i]
            if char.isupper():
                flags += 1 << i
        suffix += charset[flags]
    return id_15 + suffix


def _sanitize_for_put(entry):
    """Return a copy of an index config entry with only PUT-accepted fields."""
    return {k: v for k, v in entry.items() if k in PUT_ACCEPTED_KEYS}


def _build_metadata_index(metadata):
    """Build lookups from field metadata across all object types.

    Returns:
        by_name: dict field_name -> field_info
        by_type_name: dict (type, name) -> field_info (unambiguous)
        ambiguous_names: set of field names that appear in multiple types
    """
    by_name = {}
    ambiguous_names = set()
    by_type_name = {}
    for obj_info in metadata.get("objectInfos") or []:
        for field_info in obj_info.get("fields") or []:
            name = field_info.get("name")
            field_type = field_info.get("type")
            if not name or not field_type:
                continue
            by_type_name[(field_type, name)] = field_info
            if name in by_name:
                ambiguous_names.add(name)
            else:
                by_name[name] = field_info
    return by_name, by_type_name, ambiguous_names


def _resolve_entry(field_name, desired, by_name, by_type_name, ambiguous_names):
    """Resolve a desired config entry using metadata.

    Args:
        field_name: The field name from the config file.
        desired: Dict with isSearchable, isFacetable, facetDisplayRank, and
            optionally ``type`` to disambiguate same-name fields.
        by_name: Name-only lookup.
        by_type_name: (type, name) lookup for unambiguous resolution.
        ambiguous_names: Set of field names that exist in multiple types.

    Returns:
        Dict ready for merging into the config map, or raises ValueError.
    """
    type_hint = desired.get("type")
    if type_hint:
        meta = by_type_name.get((type_hint, field_name))
        if not meta:
            raise ValueError(
                f"Field '{field_name}' with type '{type_hint}' not found in "
                "index metadata. Is it deployed and available for indexing?"
            )
    else:
        if field_name in ambiguous_names:
            types = [t for (t, n) in by_type_name if n == field_name]
            raise ValueError(
                f"Field '{field_name}' exists in multiple types ({', '.join(types)}). "
                "Add a 'type' hint to disambiguate."
            )
        meta = by_name.get(field_name)
        if not meta:
            raise ValueError(
                f"Field '{field_name}' not found in index metadata. "
                "Is it deployed and available for indexing?"
            )

    field_type = meta["type"]
    entry = {
        "name": field_name,
        "type": field_type,
        "isSearchable": desired.get("isSearchable", True),
        "isFacetable": desired.get("isFacetable", False),
    }

    if "facetDisplayRank" in desired:
        entry["facetDisplayRank"] = desired["facetDisplayRank"]

    # Resolve the ID field based on type
    if field_type in ("Custom", "ProductAttributeDefinitionCustom"):
        custom_id = meta.get("customFieldId")
        if not custom_id:
            raise ValueError(
                f"Field '{field_name}' is {field_type} but has no customFieldId in metadata."
            )
        entry["attributeFieldId"] = _convert_15_to_18(custom_id)
    elif field_type == "ProductDynamicAttribute":
        attr_id = meta.get("attributeDefinitionId")
        if not attr_id:
            raise ValueError(
                f"Field '{field_name}' is ProductDynamicAttribute but has no "
                "attributeDefinitionId in metadata."
            )
        entry["attributeDefinitionId"] = _convert_15_to_18(attr_id)

    return entry


class ConfigureSearchIndex(BaseSalesforceApiTask):
    """Configure PCM search index fields via Connect API.

    Reads a JSON configuration file specifying which fields should be searchable
    and/or facetable, resolves their types and IDs from the API metadata, and
    merges them into the existing index configuration.  Supports Standard,
    Custom, and attribute field types.  Idempotent.
    """

    task_options = {
        "path": {
            "description": (
                "Path to the index configuration JSON file (relative to repo "
                "root or absolute). Example: datasets/search_index/guidedselling.json"
            ),
            "required": True,
        },
        "mode": {
            "description": (
                "Merge strategy: 'additive' (default) preserves existing index "
                "entries and adds/updates from the config file. 'replace' makes "
                "the config file the full desired state — entries not in the "
                "file are removed from the index. Overrides the 'mode' field in "
                "the JSON config if both are set."
            ),
            "required": False,
        },
        "raise_on_failure": {
            "description": (
                "If True (default), raise on error. Set to False to warn and "
                "continue — useful for standalone exploratory runs."
            ),
            "required": False,
        },
    }

    def _run_task(self):
        import requests

        raise_on_failure = process_bool_arg(
            self.options.get("raise_on_failure", True)
        )

        # --- Load configuration file ---
        config_path = self.options["path"]
        if not os.path.isabs(config_path):
            config_path = os.path.join(
                self.project_config.repo_root, config_path
            )

        if not os.path.isfile(config_path):
            return self._handle_failure(
                f"Configuration file not found: {config_path}",
                raise_on_failure,
            )

        with open(config_path, "r") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError as e:
                return self._handle_failure(
                    f"Invalid JSON in {config_path}: {e}", raise_on_failure
                )

        desired_fields = config.get("indexConfigurations") or []
        if not isinstance(desired_fields, list):
            return self._handle_failure(
                f"'indexConfigurations' must be an array, got {type(desired_fields).__name__}.",
                raise_on_failure,
            )
        if not desired_fields:
            self.logger.info("No fields specified in configuration — nothing to do.")
            self.return_values = {"added": [], "updated": [], "removed": [], "total_configs": 0}
            return self.return_values

        # Mode: task option overrides config file value; default additive
        mode = (self.options.get("mode") or config.get("mode") or "additive").lower()
        if mode not in ("additive", "replace"):
            return self._handle_failure(
                f"Invalid mode '{mode}'. Must be 'additive' or 'replace'.",
                raise_on_failure,
            )

        self.logger.info(
            f"Loaded {len(desired_fields)} field(s) from "
            f"{os.path.basename(config_path)} (mode={mode})"
        )

        api_version = self.project_config.project__package__api_version
        base_url = (
            f"{self.org_config.instance_url}/services/data/v{api_version}"
        )
        headers = {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }

        # --- GET current configuration with metadata ---
        self.logger.info("Retrieving current PCM index configuration...")
        try:
            get_resp = requests.get(
                f"{base_url}/{PCM_INDEX_CONFIG_PATH}?includeMetadata=true",
                headers=headers,
                timeout=60,
            )
        except requests.RequestException as e:
            return self._handle_failure(
                f"GET request failed: {e}", raise_on_failure
            )

        if get_resp.status_code < 200 or get_resp.status_code >= 300:
            return self._handle_failure(
                f"GET HTTP {get_resp.status_code} - {get_resp.text}",
                raise_on_failure,
            )

        try:
            data = get_resp.json()
        except ValueError:
            return self._handle_failure(
                "GET response was not valid JSON", raise_on_failure
            )

        existing_configs = data.get("indexConfigurations") or []
        metadata = data.get("metadata") or {}

        # --- Build metadata index for type/ID resolution ---
        by_name, by_type_name, ambiguous_names = _build_metadata_index(metadata)

        # --- Resolve desired fields against metadata ---
        resolved_entries = []
        for i, desired in enumerate(desired_fields):
            if not isinstance(desired, dict):
                return self._handle_failure(
                    f"indexConfigurations[{i}] must be an object, got {type(desired).__name__}.",
                    raise_on_failure,
                )
            field_name = desired.get("name")
            if not field_name:
                return self._handle_failure(
                    "Config entry missing 'name' field.", raise_on_failure
                )
            try:
                resolved = _resolve_entry(
                    field_name, desired, by_name, by_type_name, ambiguous_names
                )
            except ValueError as e:
                return self._handle_failure(str(e), raise_on_failure)
            resolved_entries.append(resolved)

        # --- Build merged configuration based on mode ---
        existing_keys = {(e.get("type"), e.get("name")) for e in existing_configs}

        if mode == "replace":
            config_map = {(r["type"], r["name"]): r for r in resolved_entries}
            removed = [f"{k[0]}:{k[1]}" for k in existing_keys if k not in config_map]
        else:
            config_map = {(e.get("type"), e.get("name")): dict(e) for e in existing_configs}
            for resolved in resolved_entries:
                key = (resolved["type"], resolved["name"])
                if key in config_map:
                    config_map[key].update(resolved)
                else:
                    config_map[key] = resolved
            removed = []

        added = [r["name"] for r in resolved_entries if (r["type"], r["name"]) not in existing_keys]
        updated = [r["name"] for r in resolved_entries if (r["type"], r["name"]) in existing_keys]

        # --- Sanitize and PUT ---
        put_configs = [_sanitize_for_put(e) for e in config_map.values()]
        put_body = {"indexConfigurations": put_configs}

        summary_parts = [
            f"{len(added)} added ({', '.join(added) or 'none'})",
            f"{len(updated)} updated ({', '.join(updated) or 'none'})",
        ]
        if removed:
            summary_parts.append(
                f"{len(removed)} removed ({', '.join(removed)})"
            )
        self.logger.info(
            f"Updating PCM index configuration: "
            f"{'; '.join(summary_parts)}; {len(put_configs)} total entries."
        )

        try:
            put_resp = requests.put(
                f"{base_url}/{PCM_INDEX_CONFIG_PATH}",
                headers=headers,
                json=put_body,
                timeout=60,
            )
        except requests.RequestException as e:
            return self._handle_failure(
                f"PUT request failed: {e}", raise_on_failure
            )

        if 200 <= put_resp.status_code < 300:
            self.logger.info(
                "PCM index configuration updated successfully. "
                "Run rebuild_search_index to build the index with new fields."
            )
            self.return_values = {
                "added": added,
                "updated": updated,
                "removed": removed,
                "total_configs": len(put_configs),
            }
            return self.return_values

        return self._handle_failure(
            f"PUT HTTP {put_resp.status_code} - {put_resp.text}",
            raise_on_failure,
        )

    def _handle_failure(self, detail, raise_on_failure):
        message = f"PCM index configuration failed: {detail}"
        if raise_on_failure:
            raise CumulusCIException(message)
        self.logger.warning(message + " -- continuing.")
        self.return_values = {
            "added": [], "updated": [], "removed": [], "total_configs": 0
        }
        return self.return_values


if __name__ == "__main__":
    # Offline unit tests — runnable without an org
    print("Running offline unit tests...")

    # --- Test 1: 15-to-18 char ID conversion ---
    assert _convert_15_to_18("00NEc00001Ce1Vr") == "00NEc00001Ce1VrMAJ", (
        f"Got: {_convert_15_to_18('00NEc00001Ce1Vr')}"
    )
    assert _convert_15_to_18("00NEc00001Ce1Vq") == "00NEc00001Ce1VqMAJ", (
        f"Got: {_convert_15_to_18('00NEc00001Ce1Vq')}"
    )
    assert _convert_15_to_18("00NEc00001Ce1VrMAJ") == "00NEc00001Ce1VrMAJ"
    print("  [PASS] _convert_15_to_18")

    # --- Test 2: _sanitize_for_put strips output-only fields ---
    raw_entry = {
        "attributeFieldId": "00NEc00001Ce1VrMAJ",
        "isFacetable": False,
        "isSearchable": True,
        "label": "Timeline",
        "name": "RLM_Timeline__c",
        "type": "Custom",
        "dataType": "dynamicenum",
        "extraField": "should be removed",
    }
    sanitized = _sanitize_for_put(raw_entry)
    assert sanitized == {
        "attributeFieldId": "00NEc00001Ce1VrMAJ",
        "isFacetable": False,
        "isSearchable": True,
        "name": "RLM_Timeline__c",
        "type": "Custom",
    }
    assert "label" not in sanitized
    assert "dataType" not in sanitized
    print("  [PASS] _sanitize_for_put")

    # --- Test 3: _build_metadata_index ---
    mock_metadata = {
        "objectInfos": [
            {
                "name": "Product2",
                "fields": [
                    {"name": "Name", "type": "Standard", "dataType": "text"},
                    {"name": "Family", "type": "Standard", "dataType": "dynamicenum"},
                    {
                        "name": "RLM_Timeline__c",
                        "type": "Custom",
                        "customFieldId": "00NEc00001Ce1Vr",
                        "dataType": "dynamicenum",
                    },
                    {
                        "name": "RLM_Primary_Goal__c",
                        "type": "Custom",
                        "customFieldId": "00NEc00001Ce1Vq",
                        "dataType": "multienum",
                    },
                ],
            },
            {
                "name": "ProductAttributeDefinition",
                "fields": [
                    {
                        "name": "Name",
                        "type": "ProductAttributeDefinitionStandard",
                        "dataType": "text",
                    },
                    {
                        "name": "Status",
                        "type": "ProductAttributeDefinitionStandard",
                        "dataType": "staticenum",
                    },
                    {
                        "name": "CustomAttr__c",
                        "type": "ProductAttributeDefinitionCustom",
                        "customFieldId": "00NEc00001Xy9Ab",
                        "dataType": "text",
                    },
                ],
            },
        ]
    }
    by_name, by_type_name, ambiguous_names = _build_metadata_index(mock_metadata)
    assert "Name" in ambiguous_names
    assert "Family" not in ambiguous_names
    assert by_name["Family"]["type"] == "Standard"
    assert by_name["RLM_Timeline__c"]["customFieldId"] == "00NEc00001Ce1Vr"
    assert by_name["Status"]["type"] == "ProductAttributeDefinitionStandard"
    # by_type_name has both "Name" entries
    assert by_type_name[("Standard", "Name")]["type"] == "Standard"
    assert by_type_name[("ProductAttributeDefinitionStandard", "Name")]["type"] == "ProductAttributeDefinitionStandard"
    print("  [PASS] _build_metadata_index")

    # --- Test 4: _resolve_entry for different types ---
    # Custom field (no type hint)
    resolved = _resolve_entry(
        "RLM_Timeline__c", {"isSearchable": True, "isFacetable": False},
        by_name, by_type_name, ambiguous_names,
    )
    assert resolved == {
        "name": "RLM_Timeline__c",
        "type": "Custom",
        "isSearchable": True,
        "isFacetable": False,
        "attributeFieldId": "00NEc00001Ce1VrMAJ",
    }

    # Standard field (no ID needed)
    resolved = _resolve_entry(
        "Family", {"isSearchable": True, "isFacetable": True, "facetDisplayRank": 1},
        by_name, by_type_name, ambiguous_names,
    )
    assert resolved == {
        "name": "Family",
        "type": "Standard",
        "isSearchable": True,
        "isFacetable": True,
        "facetDisplayRank": 1,
    }

    # Disambiguation with type hint: "Name" as ProductAttributeDefinitionStandard
    resolved = _resolve_entry(
        "Name", {"isSearchable": True, "isFacetable": False, "type": "ProductAttributeDefinitionStandard"},
        by_name, by_type_name, ambiguous_names,
    )
    assert resolved["type"] == "ProductAttributeDefinitionStandard"
    assert resolved["name"] == "Name"

    # Without type hint, ambiguous "Name" now raises (explicit over silent precedence)
    try:
        _resolve_entry(
            "Name", {"isSearchable": True, "isFacetable": False},
            by_name, by_type_name, ambiguous_names,
        )
        assert False, "Should have raised ValueError for ambiguous name"
    except ValueError as e:
        assert "exists in multiple types" in str(e)

    # ProductAttributeDefinitionStandard (unambiguous name, no hint needed)
    resolved = _resolve_entry(
        "Status", {"isSearchable": True, "isFacetable": True},
        by_name, by_type_name, ambiguous_names,
    )
    assert resolved == {
        "name": "Status",
        "type": "ProductAttributeDefinitionStandard",
        "isSearchable": True,
        "isFacetable": True,
    }

    # ProductAttributeDefinitionCustom resolves attributeFieldId
    resolved = _resolve_entry(
        "CustomAttr__c", {"isSearchable": True, "isFacetable": True},
        by_name, by_type_name, ambiguous_names,
    )
    assert resolved == {
        "name": "CustomAttr__c",
        "type": "ProductAttributeDefinitionCustom",
        "isSearchable": True,
        "isFacetable": True,
        "attributeFieldId": _convert_15_to_18("00NEc00001Xy9Ab"),
    }

    # Unknown field
    try:
        _resolve_entry("NonExistent__c", {"isSearchable": True}, by_name, by_type_name, ambiguous_names)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found in index metadata" in str(e)

    # Wrong type hint
    try:
        _resolve_entry("Family", {"isSearchable": True, "type": "Custom"}, by_name, by_type_name, ambiguous_names)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "with type 'Custom' not found" in str(e)
    print("  [PASS] _resolve_entry (Custom, Standard, AttributeDef, ambiguity, unknown)")

    # --- Test 5: Full merge preserves existing, adds new, strips output-only ---
    mock_existing = [
        {
            "isFacetable": False,
            "isSearchable": True,
            "label": "Product Name",
            "name": "Name",
            "type": "Standard",
        },
        {
            "attributeFieldId": "00NEc00001Ce1VrMAJ",
            "isFacetable": False,
            "isSearchable": True,
            "label": "Timeline",
            "name": "RLM_Timeline__c",
            "type": "Custom",
        },
    ]

    config_map = {}
    for entry in mock_existing:
        key = (entry.get("type"), entry.get("name"))
        config_map[key] = dict(entry)

    # Merge: update Timeline, add Family
    new_entries = [
        {"name": "RLM_Timeline__c", "type": "Custom", "isSearchable": True,
         "isFacetable": False, "attributeFieldId": "00NEc00001Ce1VrMAJ"},
        {"name": "Family", "type": "Standard", "isSearchable": True,
         "isFacetable": True, "facetDisplayRank": 1},
    ]
    for resolved in new_entries:
        key = (resolved["type"], resolved["name"])
        if key in config_map:
            config_map[key].update(resolved)
        else:
            config_map[key] = resolved

    put_configs = [_sanitize_for_put(e) for e in config_map.values()]

    # Standard "Name" preserved
    name_entries = [e for e in put_configs if e["name"] == "Name" and e["type"] == "Standard"]
    assert len(name_entries) == 1
    assert name_entries[0]["isSearchable"] is True

    # Family added with facet
    family_entries = [e for e in put_configs if e["name"] == "Family"]
    assert len(family_entries) == 1
    assert family_entries[0]["isFacetable"] is True
    assert family_entries[0]["facetDisplayRank"] == 1

    # All entries have only allowed keys
    for entry in put_configs:
        for key in entry:
            assert key in PUT_ACCEPTED_KEYS, f"Unexpected key: {key}"

    assert len(put_configs) == 3
    print("  [PASS] Full merge: preserves existing, adds Standard+Custom, strips output-only")

    # --- Test 6: Replace mode removes entries not in config ---
    mock_existing_replace = [
        {"isFacetable": False, "isSearchable": True, "label": "Product Name",
         "name": "Name", "type": "Standard"},
        {"attributeFieldId": "00NEc00001Ce1VrMAJ", "isFacetable": False,
         "isSearchable": True, "label": "Timeline",
         "name": "RLM_Timeline__c", "type": "Custom"},
        {"isFacetable": True, "isSearchable": True, "label": "Product Family",
         "name": "Family", "type": "Standard"},
    ]

    # Replace with only Timeline
    replace_resolved = [
        {"name": "RLM_Timeline__c", "type": "Custom", "isSearchable": True,
         "isFacetable": False, "attributeFieldId": "00NEc00001Ce1VrMAJ"},
    ]

    config_map_r = {}
    for r in replace_resolved:
        key = (r["type"], r["name"])
        config_map_r[key] = r

    existing_keys = {(e.get("type"), e.get("name")) for e in mock_existing_replace}
    removed_r = []
    for key in existing_keys:
        if key not in config_map_r:
            removed_r.append(f"{key[0]}:{key[1]}")

    put_configs_r = [_sanitize_for_put(e) for e in config_map_r.values()]
    assert len(put_configs_r) == 1
    assert put_configs_r[0]["name"] == "RLM_Timeline__c"
    assert len(removed_r) == 2
    assert "Standard:Name" in removed_r
    assert "Standard:Family" in removed_r
    print("  [PASS] Replace mode removes entries not in config")

    print("\nAll offline tests passed.")
