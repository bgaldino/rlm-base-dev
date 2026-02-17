"""
DEPRECATED: This standalone script has been replaced by the CCI-integrated
ExportCML task in tasks/rlm_cml.py.

Usage (new):
    cci task run export_cml --org <org_name> \\
        -o developer_name <DevName> -o version 1 \\
        -o output_dir datasets/constraints/qb/<ModelName>

This file is retained for reference only and will be removed in a future release.
"""

import subprocess
import requests
import csv
import os
import json
import argparse

# === Parse Arguments ===
parser = argparse.ArgumentParser(description="Export metadata/data for one Expression Set Definition & Version")
parser.add_argument("--developerName", type=str, required=True, help="DeveloperName of the Expression Set Definition (e.g. ProductQualification)")
parser.add_argument("--version", type=str, default="1", help="Version number (e.g. 1)")
parser.add_argument("--output-dir", type=str, default="data", help="Directory to write standard CSV exports.")
parser.add_argument("--sfdmu-dir", type=str, default="", help="Optional SFDMU dataset directory to write mapping CSVs.")
parser.add_argument("--target-org", type=str, default="srcOrg", help="Salesforce org alias to export from.")
args = parser.parse_args()
output_dir = args.output_dir
sfdmu_dir = args.sfdmu_dir.strip() or None
target_org = args.target_org.strip()

dev_name = args.developerName.strip()
version_num = args.version.strip()
api_name_versioned = f"{dev_name}_V{version_num}"

# === API Version resolver helper ===
def get_latest_api_version(instance_url):
    resp = requests.get(f"{instance_url}/services/data/")
    if resp.status_code == 200:
        versions = resp.json()
        return versions[-1]["version"]  # Use latest version
    else:
        raise Exception(f"Failed to retrieve API versions: {resp.status_code} - {resp.text}")

# === Nested child reader helper ===
def get_field_value(rec, field):
    if "." in field:
        parent, child = field.split(".", 1)
        parent_obj = rec.get(parent)
        if parent_obj and isinstance(parent_obj, dict):
            return parent_obj.get(child, "")
        return ""
    return rec.get(field, "")

# === Export CSV Helper ===
def export_to_csv(query, filename, fields, alias):
    rel_name = filename.replace(f"{output_dir}/", "")
    print(f"📦 Exporting: {rel_name}")
    print("🔍 SOQL Query:", query.strip())
    
    try:
        result = subprocess.run(
            ["sf", "org", "display", "--target-org", alias, "--json"],
            check=True,
            capture_output=True,
            text=True
        )
        org_info = json.loads(result.stdout)["result"]
        access_token = org_info["accessToken"]
        instance_url = org_info["instanceUrl"]
    except Exception as e:
        print("❌ Failed to retrieve org info from Salesforce CLI.")
        print(e)
        return False

    api_version = get_latest_api_version(instance_url)
    endpoint = f"{instance_url}/services/data/v{api_version}/query"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(endpoint, headers=headers, params={"q": query})
    if response.status_code != 200:
        print(f"❌ API Error ({filename}): {response.status_code}")
        print(response.text)
        return False

    records = response.json().get("records", [])
    print(f"✅ {len(records)} records fetched for {filename}")

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for rec in records:
            writer.writerow([get_field_value(rec, f) for f in fields])

    print(f"📄 Saved to {filename}\n")
    return True
    

# === Blob Download Helper ===
def download_constraint_model_blobs(alias, input_csv=None):
    print("📥 Downloading ConstraintModel blobs...")
    if input_csv is None:
        input_csv = os.path.join(output_dir, "ExpressionSetDefinitionVersion.csv")
    if not os.path.exists(input_csv):
        print(f"⚠️ Skipping blob download; missing {input_csv}")
        return

    try:
        result = subprocess.run(
            ["sf", "org", "display", "--target-org", alias, "--json"],
            check=True,
            capture_output=True,
            text=True
        )
        org_info = json.loads(result.stdout)["result"]
        access_token = org_info["accessToken"]
        instance_url = org_info["instanceUrl"]
        print(f"🔑 Auth success - instance: {instance_url}")
    except Exception as e:
        print("❌ Failed to get org info")
        print(e)
        return

    headers = { "Authorization": f"Bearer {access_token}" }
    os.makedirs(os.path.join(output_dir, "blobs"), exist_ok=True)

    with open(input_csv, newline='') as f:
        reader = csv.DictReader(f)
        if "ConstraintModel" not in (reader.fieldnames or []):
            print("⚠️ ConstraintModel field not available; skipping blob download.")
            return
        for row in reader:
            print(f"🧪 Row: DeveloperName={row.get('DeveloperName')}, Version={row.get('VersionNumber')}")

            if row.get("DeveloperName") != api_name_versioned:
                print("⏭️ Skipped (not matching filter)")
                continue

            blob_url = row.get("ConstraintModel", "")
            if not blob_url.startswith("/services"):
                print(f"⚠️ Invalid or empty blob URL: {blob_url}")
                continue

            full_url = instance_url + blob_url
            print(f"🌐 Fetching blob from: {full_url}")

            resp = requests.get(full_url, headers=headers)
            if resp.status_code == 200:
                file_path = os.path.join(output_dir, "blobs", f"ESDV_{dev_name}_V{version_num}.ffxblob")
                with open(file_path, "wb") as out_file:
                    out_file.write(resp.content)
                print(f"✅ Saved blob: {file_path}")
            else:
                print(f"❌ Failed to fetch blob: {resp.status_code} - {resp.text}")
                
# === Filtering Helper ===
def get_reference_ids_by_prefix(filename, prefix):
    ids = set()
    try:
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ref_id = row.get("ReferenceObjectId", "")
                if ref_id.startswith(prefix):
                    ids.add(ref_id)
    except Exception as e:
        print(f"❌ Could not process {filename} for prefix {prefix}: {e}")
    return list(ids)


def export_expression_set_definition_version():
    # Try with ConstraintModel first (industries orgs)
    primary_query = f"""
        SELECT ConstraintModel, DeveloperName, ExpressionSetDefinition.DeveloperName, ExpressionSetDefinitionId, Id, Language,
               MasterLabel, Status, VersionNumber
        FROM ExpressionSetDefinitionVersion
        WHERE ExpressionSetDefinition.DeveloperName = '{dev_name}'
          AND VersionNumber = {version_num}
    """
    primary_fields = [
        "ConstraintModel", "DeveloperName", "ExpressionSetDefinition.DeveloperName", "ExpressionSetDefinitionId", "Id", "Language",
        "MasterLabel", "Status", "VersionNumber"
    ]
    if export_to_csv(
        query=primary_query,
        filename=os.path.join(output_dir, "ExpressionSetDefinitionVersion.csv"),
        fields=primary_fields,
        alias=target_org,
    ):
        return

    # Fallback when ConstraintModel isn't supported
    fallback_query = f"""
        SELECT DeveloperName, ExpressionSetDefinition.DeveloperName, ExpressionSetDefinitionId, Id, Language,
               MasterLabel, Status, VersionNumber
        FROM ExpressionSetDefinitionVersion
        WHERE ExpressionSetDefinition.DeveloperName = '{dev_name}'
          AND VersionNumber = {version_num}
    """
    fallback_fields = [
        "DeveloperName", "ExpressionSetDefinition.DeveloperName", "ExpressionSetDefinitionId", "Id", "Language",
        "MasterLabel", "Status", "VersionNumber"
    ]
    export_to_csv(
        query=fallback_query,
        filename=os.path.join(output_dir, "ExpressionSetDefinitionVersion.csv"),
        fields=fallback_fields,
        alias=target_org,
    )


# === Begin Export Tasks ===

export_expression_set_definition_version()

export_to_csv(
    query=f"""
        SELECT ContextDefinitionApiName, ContextDefinitionId, ExpressionSetApiName, ExpressionSetDefinitionId
        FROM ExpressionSetDefinitionContextDefinition
        WHERE ExpressionSetDefinition.DeveloperName = '{dev_name}'
    """,
    filename=os.path.join(output_dir, "ExpressionSetDefinitionContextDefinition.csv"),
    fields=[
        "ContextDefinitionApiName", "ContextDefinitionId", "ExpressionSetApiName", "ExpressionSetDefinitionId"
    ],
    alias=target_org
)

export_to_csv(
    query=f"""
        SELECT ApiName, Description, ExpressionSetDefinitionId, Id,
               InterfaceSourceType, Name, ResourceInitializationType, UsageType
        FROM ExpressionSet
        WHERE ExpressionSetDefinition.DeveloperName = '{dev_name}'
    """,
    filename=os.path.join(output_dir, "ExpressionSet.csv"),
    fields=[
        "ApiName", "Description", "ExpressionSetDefinitionId", "Id",
        "InterfaceSourceType", "Name", "ResourceInitializationType", "UsageType"
    ],
    alias=target_org
)

export_to_csv(
    query=f"""
        SELECT Name, ExpressionSetId, ExpressionSet.ApiName, ReferenceObjectId, ConstraintModelTag, ConstraintModelTagType
        FROM ExpressionSetConstraintObj
        WHERE ExpressionSet.ApiName = '{dev_name}'
    """,
    filename=os.path.join(output_dir, "ExpressionSetConstraintObj.csv"),
    fields=["Name", "ExpressionSetId", "ExpressionSet.ApiName", "ReferenceObjectId", "ConstraintModelTag", "ConstraintModelTagType"],
    alias=target_org
)

# === Supporting Objects ===
# === Pull only referenced Product2, ProductClassification, and ProductRelatedComponent ===
print("🔍 Filtering ReferenceObjectIds...")

esc_path = os.path.join(output_dir, "ExpressionSetConstraintObj.csv")
if os.path.exists(esc_path):
    product_ids = get_reference_ids_by_prefix(esc_path, "01t")
    classification_ids = get_reference_ids_by_prefix(esc_path, "11B")
    component_ids = get_reference_ids_by_prefix(esc_path, "0dS")
else:
    print(f"⚠️ Skipping reference exports; missing {esc_path}")
    product_ids = []
    classification_ids = []
    component_ids = []

def build_id_query(obj_name, ids):
    if not ids:
        return f"SELECT Id, Name FROM {obj_name} WHERE Id = '000000000000000AAA'"  # dummy no-match
    joined = ",".join(f"'{x}'" for x in ids)
    return f"SELECT Id, Name FROM {obj_name} WHERE Id IN ({joined})"

# Export referenced Product2
export_to_csv(
    query=build_id_query("Product2", product_ids),
    filename=os.path.join(output_dir, "Product2.csv"),
    fields=["Id", "Name"],
    alias=target_org
)

# Export referenced ProductClassification
export_to_csv(
    query=build_id_query("ProductClassification", classification_ids),
    filename=os.path.join(output_dir, "ProductClassification.csv"),
    fields=["Id", "Name"],
    alias=target_org
)

# Export referenced ProductRelatedComponent
export_to_csv(
    query="""
        SELECT Id, Name,
               ParentProductId, ParentProduct.Name,
               ChildProductId, ChildProduct.Name,
               ChildProductClassificationId, ChildProductClassification.Name,
               ProductRelationshipTypeId, ProductRelationshipType.Name, Sequence
        FROM ProductRelatedComponent
        WHERE Id IN (%s)
    """ % ",".join(f"'{i}'" for i in component_ids) if component_ids else "SELECT Id, Name FROM ProductRelatedComponent WHERE Id = '000000000000000AAA'",
    filename=os.path.join(output_dir, "ProductRelatedComponent.csv"),
    fields=[
        "Id", "Name",
        "ParentProductId", "ParentProduct.Name",
        "ChildProductId", "ChildProduct.Name",
        "ChildProductClassificationId", "ChildProductClassification.Name",
        "ProductRelationshipTypeId", "ProductRelationshipType.Name","Sequence"
    ],
    alias=target_org
)

# === Download Blob ===
download_constraint_model_blobs(target_org)


def write_sfdmu_files():
    if not sfdmu_dir:
        return
    os.makedirs(sfdmu_dir, exist_ok=True)

    # ExpressionSet.csv (Name only)
    expr_out = os.path.join(sfdmu_dir, "ExpressionSet.csv")
    with open(expr_out, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name"])
        writer.writerow([dev_name])

    # ExpressionSetConstraintObj.csv (Name + composite external id)
    esc_in = os.path.join(output_dir, "ExpressionSetConstraintObj.csv")
    esc_out = os.path.join(sfdmu_dir, "ExpressionSetConstraintObj.csv")
    if os.path.exists(esc_in):
        with open(esc_in, newline="") as infile, open(esc_out, mode="w", newline="") as outfile:
            reader = csv.DictReader(infile)
            fieldnames = [
                "$$ConstraintModelTag$ExpressionSet.ApiName",
                "ConstraintModelTag",
                "ConstraintModelTagType",
                "CurrencyIsoCode",
                "ExpressionSet.Name",
                "ReferenceObject.Name",
            ]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                tag = row.get("ConstraintModelTag", "")
                ref_name = row.get("ReferenceObject.Name", "")
                writer.writerow({
                    "$$ConstraintModelTag$ExpressionSet.ApiName": f"{tag};{dev_name}",
                    "ConstraintModelTag": tag,
                    "ConstraintModelTagType": row.get("ConstraintModelTagType", ""),
                    "CurrencyIsoCode": row.get("CurrencyIsoCode", ""),
                    "ExpressionSet.Name": dev_name,
                    "ReferenceObject.Name": ref_name,
                })

    # Product2/ProductClassification/ProductRelatedComponent by Name only
    for name in ("Product2", "ProductClassification", "ProductRelatedComponent"):
        src = os.path.join(output_dir, f"{name}.csv")
        dest = os.path.join(sfdmu_dir, f"{name}.csv")
        if not os.path.exists(src):
            continue
        with open(src, newline="") as infile, open(dest, mode="w", newline="") as outfile:
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=["Name"])
            writer.writeheader()
            for row in reader:
                nm = row.get("Name")
                if nm:
                    writer.writerow({"Name": nm})


write_sfdmu_files()
