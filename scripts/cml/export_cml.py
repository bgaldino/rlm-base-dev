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
args = parser.parse_args()

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
def export_to_csv(query, filename, fields, alias="srcOrg"):
    print(f"📦 Exporting: {filename.replace('data/', '')}")
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
        return

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
        return

    records = response.json().get("records", [])
    print(f"✅ {len(records)} records fetched for {filename}")

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for rec in records:
            writer.writerow([get_field_value(rec, f) for f in fields])

    print(f"📄 Saved to {filename}\n")
    

# === Blob Download Helper ===
def download_constraint_model_blobs(alias="srcOrg", input_csv="data/ExpressionSetDefinitionVersion.csv"):
    print("📥 Downloading ConstraintModel blobs...")

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
    os.makedirs("data/blobs", exist_ok=True)

    with open(input_csv, newline='') as f:
        reader = csv.DictReader(f)
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
                file_path = f"data/blobs/ESDV_{dev_name}_V{version_num}.ffxblob"
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


# === Begin Export Tasks ===

export_to_csv(
    query=f"""
        SELECT ConstraintModel, DeveloperName, ExpressionSetDefinition.DeveloperName, ExpressionSetDefinitionId, Id, Language,
               MasterLabel, Status, VersionNumber
        FROM ExpressionSetDefinitionVersion
        WHERE ExpressionSetDefinition.DeveloperName = '{dev_name}'
          AND VersionNumber = {version_num}
    """,
    filename="data/ExpressionSetDefinitionVersion.csv",
    fields=[
        "ConstraintModel", "DeveloperName", "ExpressionSetDefinition.DeveloperName", "ExpressionSetDefinitionId", "Id", "Language",
        "MasterLabel", "Status", "VersionNumber"
    ]
)

export_to_csv(
    query=f"""
        SELECT ContextDefinitionApiName, ContextDefinitionId, ExpressionSetApiName, ExpressionSetDefinitionId
        FROM ExpressionSetDefinitionContextDefinition
        WHERE ExpressionSetDefinition.DeveloperName = '{dev_name}'
    """,
    filename="data/ExpressionSetDefinitionContextDefinition.csv",
    fields=[
        "ContextDefinitionApiName", "ContextDefinitionId", "ExpressionSetApiName", "ExpressionSetDefinitionId"
    ]
)

export_to_csv(
    query=f"""
        SELECT ApiName, Description, ExpressionSetDefinitionId, Id,
               InterfaceSourceType, Name, ResourceInitializationType, UsageType
        FROM ExpressionSet
        WHERE ExpressionSetDefinition.DeveloperName = '{dev_name}'
    """,
    filename="data/ExpressionSet.csv",
    fields=[
        "ApiName", "Description", "ExpressionSetDefinitionId", "Id",
        "InterfaceSourceType", "Name", "ResourceInitializationType", "UsageType"
    ]
)

export_to_csv(
    query=f"""
        SELECT Name, ExpressionSetId, ExpressionSet.ApiName, ReferenceObjectId, ConstraintModelTag, ConstraintModelTagType
        FROM ExpressionSetConstraintObj
        WHERE ExpressionSet.ApiName = '{dev_name}'
    """,
    filename="data/ExpressionSetConstraintObj.csv",
    fields=["Name", "ExpressionSetId", "ExpressionSet.ApiName", "ReferenceObjectId", "ConstraintModelTag", "ConstraintModelTagType"]
)

# === Supporting Objects ===
# === Pull only referenced Product2, ProductClassification, and ProductRelatedComponent ===
print("🔍 Filtering ReferenceObjectIds...")

product_ids = get_reference_ids_by_prefix("data/ExpressionSetConstraintObj.csv", "01t")
classification_ids = get_reference_ids_by_prefix("data/ExpressionSetConstraintObj.csv", "11B")
component_ids = get_reference_ids_by_prefix("data/ExpressionSetConstraintObj.csv", "0dS")

def build_id_query(obj_name, ids):
    if not ids:
        return f"SELECT Id, Name FROM {obj_name} WHERE Id = '000000000000000AAA'"  # dummy no-match
    joined = ",".join(f"'{x}'" for x in ids)
    return f"SELECT Id, Name FROM {obj_name} WHERE Id IN ({joined})"

# Export referenced Product2
export_to_csv(
    query=build_id_query("Product2", product_ids),
    filename="data/Product2.csv",
    fields=["Id", "Name"]
)

# Export referenced ProductClassification
export_to_csv(
    query=build_id_query("ProductClassification", classification_ids),
    filename="data/ProductClassification.csv",
    fields=["Id", "Name"]
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
    filename="data/ProductRelatedComponent.csv",
    fields=[
        "Id", "Name",
        "ParentProductId", "ParentProduct.Name",
        "ChildProductId", "ChildProduct.Name",
        "ChildProductClassificationId", "ChildProductClassification.Name",
        "ProductRelationshipTypeId", "ProductRelationshipType.Name","Sequence"
    ]
)

# === Download Blob ===
download_constraint_model_blobs()
