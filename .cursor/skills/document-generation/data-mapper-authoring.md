# Data Mapper Authoring via API

Sub-file of `document-generation/SKILL.md`. Use when creating or modifying
OmniDataTransform (ODT) records and their items programmatically via the
Salesforce REST API.

> **Scratch-org only.** The SObject API docs state OmniDataTransform/Item
> records are "for internal use only — don't perform any create, edit, or delete
> operations." The REST approach below is for **scratch-org experimentation,
> repair, and debugging**. For committed assets, author Metadata API XML under
> `unpackaged/post_docgen/omniDataTransforms/` and deploy via `prepare_docgen`.
> See the parent skill's "Supported Paths" section.

## DO NOT

- **DO NOT** use REST SObject API to create/edit/delete ODTs in shared,
  production, or customer orgs — use Metadata API XML instead.

## When to Use (Scratch-Org Only)

- Cloning an existing ODT to create a variant for quick experimentation
- Adding multiple items in bulk during prototyping
- Fixing items in a scratch org that failed creation
- Validating item structure before committing as Metadata API XML

## API Approach

Always use `sf api request rest` with a JSON body file for creating/updating
OmniDataTransformItem records. The `sf data create record --values` approach
breaks on fields containing quotes, colons, or long text.

### Create an ODT

```bash
# Write body to file
cat > /tmp/odt_body.json << 'EOF'
{
  "Name": "MyExtractODT",
  "Type": "Extract",
  "InputType": "JSON",
  "OutputType": "JSON",
  "IsActive": true,
  "IsFieldLevelSecurityEnabled": true,
  "IsNullInputsIncludedInOutput": false,
  "VersionNumber": 1
}
EOF

sf api request rest --method POST \
  --body @/tmp/odt_body.json \
  "/services/data/v67.0/sobjects/OmniDataTransform" \
  --target-org myOrg
```

For Transform ODTs, omit `InputType` and set `OutputType: "Document Template"`.

### Create an ODT Item

```bash
cat > /tmp/item_body.json << 'EOF'
{
  "Name": "myODTName",
  "OmniDataTransformationId": "0jIxxxxxxxxx",
  "InputObjectName": "Invoice",
  "InputFieldName": "Id",
  "OutputFieldName": "Invoice",
  "OutputObjectName": "json",
  "InputObjectQuerySequence": 1,
  "FilterOperator": "=",
  "FilterValue": "Id",
  "FilterGroup": "0",
  "OutputCreationSequence": 1
}
EOF

sf api request rest --method POST \
  --body @/tmp/item_body.json \
  "/services/data/v67.0/sobjects/OmniDataTransformItem" \
  --target-org myOrg
```

### Update an ODT Item

```bash
cat > /tmp/patch.json << 'EOF'
{"InputFieldName": "Invoice:PaymentTerm:Name"}
EOF

sf api request rest --method PATCH \
  --body @/tmp/patch.json \
  "/services/data/v67.0/sobjects/OmniDataTransformItem/0kdxxxxxxxxx" \
  --target-org myOrg
```

### Delete an ODT Item

```bash
sf data delete record --sobject OmniDataTransformItem \
  --record-id 0kdxxxxxxxxx --target-org myOrg
```

Note: `sf api request rest --method DELETE` requires a body argument and is
awkward; use `sf data delete record` instead.

---

## Cloning an ODT

Pattern for cloning all items from a source ODT to a new one:

```python
import json, subprocess

TARGET_ORG = "myOrg"
SOURCE_ID = "0jIxxxxxxxxx"
NEW_ID = "0jIyyyyyyyyy"

# 1. Export source items
cmd = f'sf data query -q "SELECT Name, InputFieldName, OutputFieldName, ... FROM OmniDataTransformItem WHERE OmniDataTransformationId = \'{SOURCE_ID}\'" --target-org {TARGET_ORG} --json'
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
source_items = json.loads(result.stdout)["result"]["records"]

# 2. Create each item in the new ODT
for item in source_items:
    record = {k: v for k, v in item.items()
              if v is not None and v != "" and k not in ("Id", "attributes")}
    record["OmniDataTransformationId"] = NEW_ID

    with open("/tmp/odt_item_body.json", "w") as f:
        json.dump(record, f)

    cmd = f'sf api request rest --method POST --body @/tmp/odt_item_body.json "/services/data/v67.0/sobjects/OmniDataTransformItem" --target-org {TARGET_ORG}'
    subprocess.run(cmd, shell=True, capture_output=True, text=True)
```

### Critical: Validate after cloning

After cloning, always verify:

```python
# Check for null OutputObjectName
sf data query -q "SELECT Id, OutputFieldName FROM OmniDataTransformItem
  WHERE OmniDataTransformationId = '<new_id>' AND OutputObjectName = null"

# Check for duplicates
sf data query -q "SELECT InputObjectName, OutputFieldName, FilterValue, COUNT(Id)
  FROM OmniDataTransformItem
  WHERE OmniDataTransformationId = '<new_id>' AND InputObjectName != null
  GROUP BY InputObjectName, OutputFieldName, FilterValue
  HAVING COUNT(Id) > 1"

# Compare counts
sf data query -q "SELECT COUNT(Id) FROM OmniDataTransformItem
  WHERE OmniDataTransformationId IN ('<source_id>', '<new_id>')
  GROUP BY OmniDataTransformationId"
```

---

## Wiring the DocumentTemplate

```python
def wire_template(template_id, extract_name, transform_name, target_org):
    """Wire a DocumentTemplate to its ODTs. Must deactivate first."""

    def patch(body):
        with open("/tmp/patch.json", "w") as f:
            json.dump(body, f)
        cmd = f'sf api request rest --method PATCH --body @/tmp/patch.json "/services/data/v67.0/sobjects/DocumentTemplate/{template_id}" --target-org {target_org}'
        subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # Deactivate
    patch({"IsActive": False, "Status": "Draft"})

    # Update references
    patch({
        "ExtractOmniDataTransformName": extract_name,
        "MapperOmniDataTransformName": transform_name
    })

    # Reactivate
    patch({"IsActive": True, "Status": "Active"})
```

---

## Re-toggling ODTs (Cache Refresh)

After any item changes, the ODT cache must be refreshed:

```python
def retoggle_odt(odt_id, target_org):
    """Deactivate and reactivate to flush cached item definitions."""
    for body in [{"IsActive": False}, {"IsActive": True}]:
        with open("/tmp/patch.json", "w") as f:
            json.dump(body, f)
        cmd = f'sf api request rest --method PATCH --body @/tmp/patch.json "/services/data/v67.0/sobjects/OmniDataTransform/{odt_id}" --target-org {target_org}'
        subprocess.run(cmd, shell=True, capture_output=True, text=True)
```

---

## Shell Escaping Pitfalls

**Problem:** `sf data create record --values` breaks when field values contain:
- Embedded quotes (e.g., `FilterValue: "\"Charge\""`)
- Colons in paths (e.g., `Invoice:Account:Name`)
- Special characters in formula expressions

**Solution:** Always use `sf api request rest --method POST --body @file.json`.
Write the JSON body to a temp file first. This avoids all shell escaping issues.

**Never use** `sf data create record --values` for OmniDataTransformItem records
with complex field values.

---

## Common Field Reference

### OmniDataTransform (parent record)

| Field | Extract | Transform |
|-------|---------|-----------|
| `Type` | `"Extract"` | `"Transform"` |
| `InputType` | `"JSON"` | `null` (omit) |
| `OutputType` | `"JSON"` | `"Document Template"` |
| `IsActive` | `true` | `true` |
| `IsFieldLevelSecurityEnabled` | `true` | `true` |
| `IsNullInputsIncludedInOutput` | `false` | `false` |
| `IsManagedUsingStdDesigner` | `false` | `false` |
| `TargetOutputFileName` | n/a | `"TemplateName(Version 1)"` |
| `VersionNumber` | `1` | `1` |

### OmniDataTransformItem (mandatory fields)

| Field | Required For | Notes |
|-------|-------------|-------|
| `Name` | All | Parent ODT name or descriptive name |
| `OmniDataTransformationId` | All | Parent ODT Id |
| `OutputFieldName` | All | Output key or `"Formula"` |
| `OutputObjectName` | All | Always `"json"` (or `"Formula"` for formula items) |
| `OutputCreationSequence` | All | `0` for formulas, `1` for mappings |
| `InputObjectName` | Object queries | SObject API name |
| `InputFieldName` | Object queries + field mappings | Match field or source path |
| `InputObjectQuerySequence` | Object queries | Execution order |
| `FilterOperator` | Object queries | Usually `"="` |
| `FilterValue` | Object queries | Path or literal |
| `FilterGroup` | Object queries | Usually `"0"` |

---

## Metadata API Alternative (for Committed Work)

When your ODT is ready for source control, convert it to a `.rpt-meta.xml` file.
This is the format used in `unpackaged/post_docgen/omniDataTransforms/`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<OmniDataTransform xmlns="http://soap.sforce.com/2006/04/metadata">
    <active>false</active>
    <assignmentRulesUsed>false</assignmentRulesUsed>
    <deletedOnSuccess>false</deletedOnSuccess>
    <errorIgnored>false</errorIgnored>
    <fieldLevelSecurityEnabled>false</fieldLevelSecurityEnabled>
    <inputType>JSON</inputType>
    <isManagedUsingStdDesigner>false</isManagedUsingStdDesigner>
    <name>MyExtractODT</name>
    <nullInputsIncludedInOutput>false</nullInputsIncludedInOutput>
    <omniDataTransformItem>
        <disabled>false</disabled>
        <filterGroup>0.0</filterGroup>
        <globalKey>unique-guid-here</globalKey>
        <inputFieldName>Invoice:Account:Name</inputFieldName>
        <inputObjectQuerySequence>0.0</inputObjectQuerySequence>
        <linkedObjectSequence>0.0</linkedObjectSequence>
        <name>MyExtractODT</name>
        <outputCreationSequence>1.0</outputCreationSequence>
        <outputFieldName>AccountName</outputFieldName>
        <outputObjectName>json</outputObjectName>
        <requiredForUpsert>false</requiredForUpsert>
        <transformValuesMappings>{ }</transformValuesMappings>
        <upsertKey>false</upsertKey>
    </omniDataTransformItem>
    <!-- more items... -->
    <outputType>JSON</outputType>
    <type>Extract</type>
    <versionNumber>1.0</versionNumber>
</OmniDataTransform>
```

Retrieve from an org with:
```bash
sf project retrieve start --metadata OmniDataTransform:MyExtractODT --target-org <alias>
```

Deploy via `prepare_docgen` flow or directly:
```bash
sf project deploy start --source-dir unpackaged/post_docgen/omniDataTransforms/ --target-org <alias>
```

See `docs/guides/docgen-setup.md` for the full deployment sequence including
formula field pre-deploy, ODT seed workaround, and binary fix.
