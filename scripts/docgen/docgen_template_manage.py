"""
Manage DocumentTemplate lifecycle programmatically via Salesforce REST/CLI.

Supports the full template lifecycle: list, inspect, activate/deactivate,
upload/replace binary, create new templates, and download source or output files.

Usage:
  python scripts/docgen/docgen_template_manage.py list --org dev-scratch
  python scripts/docgen/docgen_template_manage.py status RLM_QuoteProposal --org dev-scratch
  python scripts/docgen/docgen_template_manage.py deactivate RLM_QuoteProposal --org dev-scratch
  python scripts/docgen/docgen_template_manage.py activate RLM_QuoteProposal --org dev-scratch
  python scripts/docgen/docgen_template_manage.py upload RLM_QuoteProposal template.docx --org dev-scratch
  python scripts/docgen/docgen_template_manage.py replace RLM_QuoteProposal template.docx --org dev-scratch
  python scripts/docgen/docgen_template_manage.py create RLM_NewTemplate template.docx --org dev-scratch --extract-odt RLMQuoteProposalExtract --transform-odt RLMQuoteProposalTransform --activate
  python scripts/docgen/docgen_template_manage.py update RLM_QuoteProposal --org dev-scratch --extract-odt RLMQuoteProposalExtractV2
  python scripts/docgen/docgen_template_manage.py download --template RLM_QuoteProposal --org dev-scratch --output template.docx
  python scripts/docgen/docgen_template_manage.py download --version-id 068XXXXXXXXXXXXAAA --org dev-scratch --output output.pdf
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile

from _soql import soql_escape

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests",
          file=sys.stderr)
    sys.exit(1)


LIBRARY_DEV_NAME = "DocgenDocumentTemplateLibrary"

TEMPLATE_FIELDS = (
    "Id, Name, VersionNumber, IsActive, Status, Type, UsageType, "
    "ExtractOmniDataTransformName, MapperOmniDataTransformName, "
    "TokenMappingMethodType, DocumentGenerationMechanism, TokenList"
)


def _sf_query(query, org):
    """Run SOQL query via sf CLI, return records list or None on error."""
    result = subprocess.run(
        ["sf", "data", "query", "-q", query, "--target-org", org, "--json"],
        capture_output=True, text=True,
    )
    try:
        data = json.loads(result.stdout)
        if data.get("status") != 0:
            msg = data.get("message", data.get("name", "unknown error"))
            print(f"QUERY ERROR: {msg}", file=sys.stderr)
            return None
        return data["result"]["records"]
    except (json.JSONDecodeError, KeyError):
        print(f"ERROR: Failed to parse query result: {result.stderr or result.stdout}",
              file=sys.stderr)
        return None


def _sf_update(sobject, record_id, values_str, org):
    """Update a record via sf data update record. Returns True on success."""
    result = subprocess.run(
        ["sf", "data", "update", "record", "--sobject", sobject,
         "--record-id", record_id, "--values", values_str,
         "--target-org", org, "--json"],
        capture_output=True, text=True,
    )
    try:
        data = json.loads(result.stdout)
        if data.get("status") == 0 and data.get("result", {}).get("success"):
            return True
        msg = data.get("message", "")
        if not msg and "data" in data:
            msg = data["data"].get("message", "")
        print(f"UPDATE ERROR: {msg}", file=sys.stderr)
        return False
    except (json.JSONDecodeError, KeyError):
        print(f"ERROR: {result.stderr or result.stdout}", file=sys.stderr)
        return False


def _get_rest_auth(org):
    """Get instance_url and access_token from sf org display --json."""
    result = subprocess.run(
        ["sf", "org", "display", "--target-org", org, "--json"],
        capture_output=True, text=True,
    )
    try:
        data = json.loads(result.stdout)
        info = data.get("result", {})
        token = info.get("accessToken")
        url = info.get("instanceUrl")
        if not token or not url:
            print("ERROR: Could not get accessToken/instanceUrl from sf org display. "
                  "Ensure the org is authenticated and the alias is correct.",
                  file=sys.stderr)
            sys.exit(1)
        return url, token
    except (json.JSONDecodeError, KeyError):
        print(f"ERROR: Failed to parse sf org display output: {result.stderr}",
              file=sys.stderr)
        sys.exit(1)


def _find_library(org):
    """Find the DocGen ContentWorkspace library Id."""
    records = _sf_query(
        f"SELECT Id FROM ContentWorkspace "
        f"WHERE DeveloperName = '{LIBRARY_DEV_NAME}' LIMIT 1", org
    )
    if not records:
        print(f"ERROR: ContentWorkspace '{LIBRARY_DEV_NAME}' not found. "
              f"Run create_docgen_library first.", file=sys.stderr)
        sys.exit(1)
    return records[0]["Id"]


def _resolve_template(name_or_id, org, require_unique=True):
    """Resolve a template by Name or Id. Returns record dict or exits."""
    if name_or_id.startswith("2dt"):
        if not re.match(r'^[a-zA-Z0-9]{15,18}$', name_or_id):
            print(f"ERROR: Invalid Salesforce Id format: '{name_or_id}'", file=sys.stderr)
            sys.exit(1)
        safe_id = soql_escape(name_or_id)
        records = _sf_query(
            f"SELECT {TEMPLATE_FIELDS} FROM DocumentTemplate "
            f"WHERE Id = '{safe_id}' LIMIT 1", org
        )
    else:
        safe_name = soql_escape(name_or_id)
        records = _sf_query(
            f"SELECT {TEMPLATE_FIELDS} FROM DocumentTemplate "
            f"WHERE Name = '{safe_name}' ORDER BY VersionNumber DESC", org
        )

    if not records:
        print(f"ERROR: DocumentTemplate '{name_or_id}' not found.", file=sys.stderr)
        available = _sf_query(
            "SELECT Name, VersionNumber, Status FROM DocumentTemplate "
            "ORDER BY Name", org
        )
        if available:
            print("\nAvailable templates:", file=sys.stderr)
            for r in available:
                print(f"  {r['Name']} (v{r['VersionNumber']}, {r['Status']})",
                      file=sys.stderr)
        sys.exit(1)

    if len(records) > 1 and require_unique:
        print(f"ERROR: Multiple DocumentTemplate records match '{name_or_id}':",
              file=sys.stderr)
        for r in records:
            print(f"  {r['Id']}  {r['Name']} v{r['VersionNumber']} ({r['Status']})",
                  file=sys.stderr)
        print(f"\nUse --template-id <2dt...> to specify exactly which one.",
              file=sys.stderr)
        sys.exit(1)

    return records[0]


def _find_content_doc(template_name, library_id, org, content_doc_id_override=None):
    """Find the ContentDocumentId for a template in the DocGen library."""
    if content_doc_id_override:
        return content_doc_id_override

    safe_name = soql_escape(template_name)
    records = _sf_query(
        f"SELECT Id FROM ContentDocument "
        f"WHERE Title = '{safe_name}' "
        f"AND Id IN (SELECT ContentDocumentId FROM ContentWorkspaceDoc "
        f"WHERE ContentWorkspaceId = '{library_id}') "
        f"ORDER BY CreatedDate DESC LIMIT 1", org
    )
    if records:
        return records[0]["Id"]

    records = _sf_query(
        f"SELECT Id, Title FROM ContentDocument "
        f"WHERE Title LIKE '{safe_name}%' "
        f"AND Id IN (SELECT ContentDocumentId FROM ContentWorkspaceDoc "
        f"WHERE ContentWorkspaceId = '{library_id}') "
        f"ORDER BY CreatedDate DESC LIMIT 3", org
    )
    if records:
        if len(records) == 1:
            print(f"  WARNING: Exact title match failed, using partial: "
                  f"'{records[0]['Title']}'", file=sys.stderr)
            return records[0]["Id"]
        print(f"ERROR: No exact title match for '{template_name}' in library. "
              f"Partial matches:", file=sys.stderr)
        for r in records:
            print(f"  {r['Id']}  {r['Title']}", file=sys.stderr)
        print(f"\nUse --content-doc-id <069...> to specify explicitly.",
              file=sys.stderr)
        sys.exit(1)

    print(f"ERROR: No ContentDocument found for '{template_name}' in the DocGen library.",
          file=sys.stderr)
    sys.exit(1)


def _validate_file(file_path):
    """Validate that the file exists and is a valid ZIP (DOCX)."""
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    with open(file_path, "rb") as f:
        magic = f.read(4)
    if magic != b"PK\x03\x04":
        print(f"ERROR: File is not a valid ZIP/DOCX: {file_path}", file=sys.stderr)
        sys.exit(1)
    return os.path.getsize(file_path)


# --- Commands ---

def cmd_list(args):
    """List all DocumentTemplates in the org."""
    records = _sf_query(
        f"SELECT {TEMPLATE_FIELDS} FROM DocumentTemplate ORDER BY Name, VersionNumber DESC",
        args.org
    )
    if not records:
        print("No DocumentTemplates found.")
        return

    if args.json_output:
        for r in records:
            r.pop("attributes", None)
        print(json.dumps(records, indent=2))
        return

    print(f"{'Name':<40} {'Ver':>3} {'Status':<8} {'Type':<15} {'Usage':<30} {'Extract ODT'}")
    print("-" * 130)
    for r in records:
        r.pop("attributes", None)
        print(f"{r['Name']:<40} {r['VersionNumber']:>3} {r['Status']:<8} "
              f"{r['Type']:<15} {r.get('UsageType') or '':<30} "
              f"{r.get('ExtractOmniDataTransformName') or ''}")


def cmd_status(args):
    """Show detailed status for a single template."""
    template = _resolve_template(args.name, args.org, require_unique=False)
    template.pop("attributes", None)

    if args.json_output:
        print(json.dumps(template, indent=2))
        return

    print(f"Template: {template['Name']}")
    print(f"  Id:                {template['Id']}")
    print(f"  Version:           {template['VersionNumber']}")
    print(f"  Status:            {template['Status']} (IsActive={template['IsActive']})")
    print(f"  Type:              {template['Type']}")
    print(f"  Usage:             {template.get('UsageType') or 'N/A'}")
    print(f"  Mechanism:         {template.get('DocumentGenerationMechanism') or 'N/A'}")
    print(f"  Mapping Method:    {template.get('TokenMappingMethodType') or 'N/A'}")
    print(f"  Extract ODT:       {template.get('ExtractOmniDataTransformName') or 'N/A'}")
    print(f"  Transform ODT:     {template.get('MapperOmniDataTransformName') or 'N/A'}")
    token_list = template.get("TokenList") or ""
    token_count = len(token_list.split(",")) if token_list else 0
    print(f"  Tokens:            {token_count} mapped")

    library_id = _find_library(args.org)
    try:
        doc_id = _find_content_doc(template["Name"], library_id, args.org)
        cv_records = _sf_query(
            f"SELECT Id, VersionNumber, ContentSize, CreatedDate FROM ContentVersion "
            f"WHERE ContentDocumentId = '{doc_id}' ORDER BY VersionNumber DESC LIMIT 3",
            args.org
        )
        if cv_records:
            print(f"\n  ContentDocument:   {doc_id}")
            print(f"  Latest versions:")
            for cv in cv_records:
                size_kb = cv["ContentSize"] // 1024
                print(f"    v{cv['VersionNumber']}: {cv['Id']} ({size_kb}KB, {cv['CreatedDate']})")
    except SystemExit:
        print(f"\n  ContentDocument:   NOT FOUND in library")


def cmd_deactivate(args):
    """Deactivate a template (IsActive=false, Status=Draft)."""
    template = _resolve_template(args.template_id or args.name, args.org, require_unique=True)
    if not template["IsActive"]:
        print(f"Template '{template['Name']}' is already inactive (Status={template['Status']}).")
        return

    print(f"Deactivating: {template['Name']} (v{template['VersionNumber']})")
    success = _sf_update("DocumentTemplate", template["Id"],
                         "IsActive=false Status=Draft", args.org)
    if success:
        print(f"  Done. Status: Draft")
    else:
        sys.exit(1)


def cmd_activate(args):
    """Activate a template (IsActive=true, Status=Active)."""
    template = _resolve_template(args.template_id or args.name, args.org, require_unique=True)
    if template["IsActive"]:
        print(f"Template '{template['Name']}' is already active.")
        return

    print(f"Activating: {template['Name']} (v{template['VersionNumber']})")
    success = _sf_update("DocumentTemplate", template["Id"],
                         "IsActive=true Status=Active", args.org)
    if success:
        print(f"  Done. Status: Active")
    else:
        sys.exit(1)


def cmd_upload(args):
    """Upload a new binary to an existing template's ContentDocument."""
    file_size = _validate_file(args.file)
    template = _resolve_template(args.template_id or args.name, args.org, require_unique=True)
    library_id = _find_library(args.org)
    doc_id = _find_content_doc(template["Name"], library_id, args.org, args.content_doc_id)

    print(f"Uploading to: {template['Name']} (ContentDocument: {doc_id})")
    print(f"  File: {args.file} ({file_size // 1024}KB)")

    instance_url, token = _get_rest_auth(args.org)
    with open(args.file, "rb") as f:
        version_data = base64.b64encode(f.read()).decode("utf-8")

    resp = requests.post(
        f"{instance_url}/services/data/v67.0/sobjects/ContentVersion",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "ContentDocumentId": doc_id,
            "Title": template["Name"],
            "PathOnClient": f"{template['Name']}.docx",
            "VersionData": version_data,
        },
    )

    if resp.status_code == 201:
        cv_id = resp.json()["id"]
        print(f"  Created ContentVersion: {cv_id}")
    else:
        print(f"ERROR: Upload failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)


def cmd_create(args):
    """Create a new DocumentTemplate and upload the .docx to the library."""
    file_size = _validate_file(args.file)
    library_id = _find_library(args.org)

    existing = _sf_query(
        f"SELECT Id, Name FROM DocumentTemplate WHERE Name = '{args.name.replace(chr(39), chr(92)+chr(39))}'",
        args.org
    )
    if existing:
        print(f"ERROR: DocumentTemplate '{args.name}' already exists (Id: {existing[0]['Id']}). "
              f"Use 'upload' to replace its binary.", file=sys.stderr)
        sys.exit(1)

    print(f"Creating template: {args.name}")
    print(f"  File: {args.file} ({file_size // 1024}KB)")

    instance_url, token = _get_rest_auth(args.org)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    with open(args.file, "rb") as f:
        version_data = base64.b64encode(f.read()).decode("utf-8")

    cv_resp = requests.post(
        f"{instance_url}/services/data/v67.0/sobjects/ContentVersion",
        headers=headers,
        json={
            "Title": args.name,
            "PathOnClient": f"{args.name}.docx",
            "VersionData": version_data,
            "FirstPublishLocationId": library_id,
        },
    )
    if cv_resp.status_code != 201:
        print(f"ERROR: File upload failed ({cv_resp.status_code}): {cv_resp.text}",
              file=sys.stderr)
        sys.exit(1)
    cv_id = cv_resp.json()["id"]
    print(f"  Uploaded to library: ContentVersion {cv_id}")

    dt_body = {
        "Name": args.name,
        "Type": "MicrosoftWord",
        "TokenMappingType": "JSON",
        "Status": "Draft",
        "IsActive": False,
        "DocumentGenerationMechanism": args.mechanism or "ServerSide",
        "TokenMappingMethodType": args.mapping_method or "OmniDataTransform",
    }
    if args.extract_odt:
        dt_body["ExtractOmniDataTransformName"] = args.extract_odt
    if args.transform_odt:
        dt_body["MapperOmniDataTransformName"] = args.transform_odt
    if args.usage_type:
        dt_body["UsageType"] = args.usage_type

    dt_resp = requests.post(
        f"{instance_url}/services/data/v67.0/sobjects/DocumentTemplate",
        headers=headers,
        json=dt_body,
    )
    if dt_resp.status_code != 201:
        print(f"ERROR: DocumentTemplate creation failed ({dt_resp.status_code}): {dt_resp.text}",
              file=sys.stderr)
        sys.exit(1)
    dt_id = dt_resp.json()["id"]
    print(f"  Created DocumentTemplate: {dt_id}")

    if args.activate:
        print(f"  Activating...")
        activate_resp = requests.patch(
            f"{instance_url}/services/data/v67.0/sobjects/DocumentTemplate/{dt_id}",
            headers=headers,
            json={"IsActive": True, "Status": "Active"},
        )
        if activate_resp.status_code == 204:
            print(f"  Status: Active")
        else:
            print(f"  WARNING: Activation failed ({activate_resp.status_code}): "
                  f"{activate_resp.text}", file=sys.stderr)
    else:
        print(f"  Status: Draft (use 'activate' to make it live)")


def cmd_update(args):
    """Update template metadata fields."""
    template = _resolve_template(args.template_id or args.name, args.org, require_unique=True)

    updates = []
    if args.extract_odt is not None:
        updates.append(f"ExtractOmniDataTransformName={args.extract_odt}")
    if args.transform_odt is not None:
        updates.append(f"MapperOmniDataTransformName={args.transform_odt}")
    if args.usage_type is not None:
        updates.append(f"UsageType={args.usage_type}")
    if args.mechanism is not None:
        updates.append(f"DocumentGenerationMechanism={args.mechanism}")
    if args.mapping_method is not None:
        updates.append(f"TokenMappingMethodType={args.mapping_method}")

    if not updates:
        print("ERROR: No fields to update. Use --extract-odt, --transform-odt, "
              "--usage-type, --mechanism, or --mapping-method.", file=sys.stderr)
        sys.exit(1)

    values_str = " ".join(updates)
    print(f"Updating: {template['Name']} ({template['Id']})")
    print(f"  Fields: {values_str}")

    success = _sf_update("DocumentTemplate", template["Id"], values_str, args.org)
    if success:
        print(f"  Done.")
    else:
        sys.exit(1)


def cmd_replace(args):
    """Full lifecycle: deactivate -> upload -> reactivate."""
    file_size = _validate_file(args.file)
    template = _resolve_template(args.template_id or args.name, args.org, require_unique=True)
    library_id = _find_library(args.org)
    doc_id = _find_content_doc(template["Name"], library_id, args.org, args.content_doc_id)

    print(f"Replace lifecycle for: {template['Name']}")
    print(f"  File: {args.file} ({file_size // 1024}KB)")

    was_active = template["IsActive"]
    if was_active:
        print(f"  Step 1: Deactivating...")
        success = _sf_update("DocumentTemplate", template["Id"],
                             "IsActive=false Status=Draft", args.org)
        if not success:
            print("ERROR: Deactivation failed, aborting.", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"  Step 1: Already inactive, skipping deactivation")

    print(f"  Step 2: Uploading binary...")
    instance_url, token = _get_rest_auth(args.org)
    with open(args.file, "rb") as f:
        version_data = base64.b64encode(f.read()).decode("utf-8")

    resp = requests.post(
        f"{instance_url}/services/data/v67.0/sobjects/ContentVersion",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "ContentDocumentId": doc_id,
            "Title": template["Name"],
            "PathOnClient": f"{template['Name']}.docx",
            "VersionData": version_data,
        },
    )
    if resp.status_code != 201:
        print(f"ERROR: Upload failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        if was_active:
            print("  Attempting to reactivate after failed upload...", file=sys.stderr)
            _sf_update("DocumentTemplate", template["Id"],
                       "IsActive=true Status=Active", args.org)
        sys.exit(1)
    cv_id = resp.json()["id"]
    print(f"    ContentVersion: {cv_id}")

    if was_active:
        print(f"  Step 3: Reactivating...")
        success = _sf_update("DocumentTemplate", template["Id"],
                             "IsActive=true Status=Active", args.org)
        if success:
            print(f"  Done. Template replaced and reactivated.")
        else:
            print(f"  WARNING: Upload succeeded but reactivation failed. "
                  f"Run 'activate {template['Name']}' manually.", file=sys.stderr)
    else:
        print(f"  Done. Template binary replaced (remains inactive).")


def cmd_download(args):
    """Download a template .docx or any ContentVersion by ID."""
    instance_url, token = _get_rest_auth(args.org)
    headers = {"Authorization": f"Bearer {token}"}

    if args.version_id:
        cv_id = args.version_id
        if not cv_id.startswith("068"):
            print(f"ERROR: --version-id must be a ContentVersion ID (068 prefix), "
                  f"got: {cv_id}", file=sys.stderr)
            sys.exit(1)
        cv_records = _sf_query(
            f"SELECT Title, FileExtension FROM ContentVersion WHERE Id = '{cv_id}'",
            args.org
        )
        title = cv_records[0]["Title"] if cv_records else "download"
        ext = cv_records[0].get("FileExtension", "bin") if cv_records else "bin"
        default_filename = f"{title}.{ext}"
    elif args.template:
        template = _resolve_template(args.template, args.org, require_unique=False)
        library_id = _find_library(args.org)
        doc_id = _find_content_doc(template["Name"], library_id, args.org)
        cv_records = _sf_query(
            f"SELECT Id FROM ContentVersion "
            f"WHERE ContentDocumentId = '{doc_id}' "
            f"ORDER BY VersionNumber DESC LIMIT 1", args.org
        )
        if not cv_records:
            print(f"ERROR: No ContentVersion found for ContentDocument {doc_id}",
                  file=sys.stderr)
            sys.exit(1)
        cv_id = cv_records[0]["Id"]
        default_filename = f"{template['Name']}.docx"
    else:
        print("ERROR: Specify --template <name> or --version-id <068XXXXXXXXXXXXAAA>",
              file=sys.stderr)
        sys.exit(1)

    output_path = args.output or default_filename
    print(f"Downloading ContentVersion {cv_id} -> {output_path}")

    resp = requests.get(
        f"{instance_url}/services/data/v67.0/sobjects/ContentVersion/{cv_id}/VersionData",
        headers=headers,
    )
    if resp.status_code != 200:
        print(f"ERROR: Download failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)

    if os.path.exists(output_path) and not os.environ.get("DOCGEN_FORCE_OVERWRITE"):
        print(f"ERROR: '{output_path}' already exists. Set DOCGEN_FORCE_OVERWRITE=1 or choose a different --output path.",
              file=sys.stderr)
        sys.exit(1)

    with open(output_path, "wb") as f:
        f.write(resp.content)
    print(f"  Saved: {output_path} ({len(resp.content) // 1024}KB)")


def main():
    parser = argparse.ArgumentParser(
        description="Manage DocumentTemplate lifecycle (list, activate, upload, download)"
    )
    subparsers = parser.add_subparsers(dest="command")

    # list
    list_p = subparsers.add_parser("list", help="List all DocumentTemplates")
    list_p.add_argument("--org", required=True, help="SF CLI target org alias")
    list_p.add_argument("--json", action="store_true", dest="json_output")

    # status
    status_p = subparsers.add_parser("status", help="Show template detail")
    status_p.add_argument("name", help="Template name or Id (2dt...)")
    status_p.add_argument("--org", required=True, help="SF CLI target org alias")
    status_p.add_argument("--json", action="store_true", dest="json_output")

    # deactivate
    deact_p = subparsers.add_parser("deactivate", help="Deactivate a template")
    deact_p.add_argument("name", help="Template name or Id")
    deact_p.add_argument("--org", required=True, help="SF CLI target org alias")
    deact_p.add_argument("--template-id", help="Explicit template Id for disambiguation")

    # activate
    act_p = subparsers.add_parser("activate", help="Activate a template")
    act_p.add_argument("name", help="Template name or Id")
    act_p.add_argument("--org", required=True, help="SF CLI target org alias")
    act_p.add_argument("--template-id", help="Explicit template Id for disambiguation")

    # upload
    up_p = subparsers.add_parser("upload", help="Upload new binary to existing template")
    up_p.add_argument("name", help="Template name or Id")
    up_p.add_argument("file", help="Path to .docx or .dt file")
    up_p.add_argument("--org", required=True, help="SF CLI target org alias")
    up_p.add_argument("--template-id", help="Explicit template Id for disambiguation")
    up_p.add_argument("--content-doc-id", help="Explicit ContentDocument Id (069...)")

    # create
    cr_p = subparsers.add_parser("create", help="Create new template + upload file")
    cr_p.add_argument("name", help="Template name")
    cr_p.add_argument("file", help="Path to .docx or .dt file")
    cr_p.add_argument("--org", required=True, help="SF CLI target org alias")
    cr_p.add_argument("--extract-odt", help="Extract ODT name")
    cr_p.add_argument("--transform-odt", help="Transform ODT name")
    cr_p.add_argument("--usage-type", help="Usage type (Revenue_Lifecycle_Management, Invoice, etc.)")
    cr_p.add_argument("--mechanism", help="ServerSide or ClientSide (default: ServerSide)")
    cr_p.add_argument("--mapping-method", help="OmniDataTransform or ContextService")
    cr_p.add_argument("--activate", action="store_true", help="Activate immediately after creation")

    # update
    upd_p = subparsers.add_parser("update", help="Update template metadata fields")
    upd_p.add_argument("name", help="Template name or Id")
    upd_p.add_argument("--org", required=True, help="SF CLI target org alias")
    upd_p.add_argument("--template-id", help="Explicit template Id for disambiguation")
    upd_p.add_argument("--extract-odt", help="Extract ODT name")
    upd_p.add_argument("--transform-odt", help="Transform ODT name")
    upd_p.add_argument("--usage-type", help="Usage type")
    upd_p.add_argument("--mechanism", help="ServerSide or ClientSide")
    upd_p.add_argument("--mapping-method", help="OmniDataTransform or ContextService")

    # replace
    rep_p = subparsers.add_parser("replace", help="Full lifecycle: deactivate -> upload -> reactivate")
    rep_p.add_argument("name", help="Template name or Id")
    rep_p.add_argument("file", help="Path to .docx or .dt file")
    rep_p.add_argument("--org", required=True, help="SF CLI target org alias")
    rep_p.add_argument("--template-id", help="Explicit template Id for disambiguation")
    rep_p.add_argument("--content-doc-id", help="Explicit ContentDocument Id (069...)")

    # download
    dl_p = subparsers.add_parser("download", help="Download template .docx or ContentVersion")
    dl_p.add_argument("--template", help="Template name to download source .docx")
    dl_p.add_argument("--version-id", help="ContentVersion Id (068XXXXXXXXXXXXAAA) to download directly")
    dl_p.add_argument("--org", required=True, help="SF CLI target org alias")
    dl_p.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "list": cmd_list,
        "status": cmd_status,
        "deactivate": cmd_deactivate,
        "activate": cmd_activate,
        "upload": cmd_upload,
        "create": cmd_create,
        "update": cmd_update,
        "replace": cmd_replace,
        "download": cmd_download,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
