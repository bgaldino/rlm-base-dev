"""
DEPRECATED: This standalone script has been replaced by the CCI-integrated
ImportCML task in tasks/rlm_cml.py.

Usage (new):
    cci task run import_cml --org <org_name> \\
        -o data_dir datasets/constraints/qb/<ModelName>

This file is retained for reference only and will be removed in a future release.
"""

import argparse
import os
import csv
import json
import requests
import subprocess

DEFAULT_DATA_DIR = "data"
TARGET_ALIAS = "tgtOrg"


def parse_args():
    parser = argparse.ArgumentParser(description="Import CML metadata and data into a target org.")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR, help="Directory containing CML CSV exports.")
    parser.add_argument("--dataset-dir", action="append", default=[], help="SFDMU dataset directory for ExpressionSetConstraintObj mapping.")
    parser.add_argument("--target-org", default=TARGET_ALIAS, help="Target org alias (Salesforce CLI).")
    return parser.parse_args()

access_token = None
instance_url = None
api_version = None
headers = {}

def get_latest_api_version(instance_url):
    resp = requests.get(f"{instance_url}/services/data/")
    if resp.status_code == 200:
        versions = resp.json()
        return versions[-1]["version"]  # The last one is the latest
    else:
        raise Exception(f"Failed to retrieve API versions: {resp.status_code} - {resp.text}")

# === Auth + Org Info ===
def get_auth(target_alias):
    result = subprocess.run(
        ["sf", "org", "display", "--target-org", target_alias, "--json"],
        check=True,
        capture_output=True,
        text=True
    )
    info = json.loads(result.stdout)["result"]
    return info["accessToken"], info["instanceUrl"]

# === CSV Loader ===
def read_csv(filename, data_dir):
    with open(os.path.join(data_dir, filename), newline="") as f:
        return list(csv.DictReader(f))


def read_csv_optional(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def build_name_set(rows, key):
    return {row.get(key, "").strip() for row in rows if row.get(key, "").strip()}


def resolve_name_map(instance_url, api_version, access_token, obj_name, names):
    if not names:
        return {}
    query_url = f"{instance_url}/services/data/v{api_version}/query"
    headers = {"Authorization": f"Bearer {access_token}"}
    name_filter = ",".join(f"'{n}'" for n in names)
    soql = f"SELECT Id, Name FROM {obj_name} WHERE Name IN ({name_filter})"
    resp = requests.get(query_url, headers=headers, params={"q": soql})
    if resp.status_code != 200:
        print(f"❌ Failed to query {obj_name} by Name: {resp.status_code} - {resp.text}")
        return {}
    return {r["Name"]: r["Id"] for r in resp.json().get("records", [])}

# === REST: POST ===
def create_record(obj_name, record, access_token, instance_url, api_version):
    url = f"{instance_url}/services/data/v{api_version}/sobjects/{obj_name}/"

    record.pop("Id", None)
    resp = requests.post(url, headers=headers, json=record)
    if resp.status_code == 201:
        print(f"✅ Created {obj_name} → {record.get('Name', record.get('ApiName', '') )}")
        return resp.json()["id"]
    else:
        print(f"❌ Failed {obj_name}: {resp.status_code} - {resp.text}")
        return None
    
def upsert_expression_set(record, access_token, instance_url, api_version):
    obj_name = "ExpressionSet"
    api_name = record.get("ApiName")
    if not api_name:
        print("❌ ExpressionSet record missing ApiName. Skipping.")
        return None

    # Query to see if the ExpressionSet exists
    query_url = f"{instance_url}/services/data/v{api_version}/query"
    soql = f"SELECT Id FROM {obj_name} WHERE ApiName = '{api_name}'"
    resp = requests.get(query_url, headers=headers, params={"q": soql})

    if resp.status_code != 200:
        print(f"❌ Failed to query for ExpressionSet {api_name}: {resp.status_code} - {resp.text}")
        return None

    records = resp.json().get("records", [])
    record.pop("ExpressionSetDefinitionId", None)
    
    if records:
        # UPDATE (PATCH)
        record_id = records[0]["Id"]
        patch_url = f"{instance_url}/services/data/v{api_version}/sobjects/{obj_name}/{record_id}"
        record.pop("ApiName", None)  # Don't include ApiName in the body
        patch_resp = requests.patch(patch_url, headers=headers, json=record)
        record["ApiName"] = api_name  # 👈 Put it back
        if patch_resp.status_code in [204, 200]:
            print(f"🔁 Updated ExpressionSet → {api_name}")
            return record_id
        else:
            print(f"❌ Failed to update ExpressionSet: {patch_resp.status_code} - {patch_resp.text}")
            return None
    else:
        # CREATE (POST)
        print(f"➕ Creating new ExpressionSet → {api_name}")
        return create_record(obj_name, record, access_token, instance_url, api_version)


def upsert_esdcd(record, access_token, instance_url, api_version):
    obj_name = "ExpressionSetDefinitionContextDefinition"
    context_id = record.get("ContextDefinitionId")
    esd_id = record.get("ExpressionSetDefinitionId")

    if not context_id or not esd_id:
        print("❌ Missing ContextDefinitionId or ExpressionSetDefinitionId for ESDCD.")
        return None

    # Query for existence
    soql = f"""
        SELECT Id FROM {obj_name}
        WHERE ExpressionSetDefinitionId = '{esd_id}'
    """
    query_url = f"{instance_url}/services/data/v{api_version}/query"
    resp = requests.get(query_url, headers=headers, params={"q": soql.strip()})

    if resp.status_code != 200:
        print(f"❌ Query failed for ESDCD: {resp.status_code} - {resp.text}")
        return None

    found = resp.json().get("records", [])

    if found:
        record_id = found[0]["Id"]
        print("✅ ExpressionSetDefinitionContextDefinition already exists. Updating ContextDefinitionId...")

        # Only update ContextDefinitionId
        patch_url = f"{instance_url}/services/data/v{api_version}/sobjects/{obj_name}/{record_id}"
        patch_body = { "ContextDefinitionId": context_id }

        patch_resp = requests.patch(patch_url, headers=headers, json=patch_body)
        if patch_resp.status_code in [200, 204]:
            print(f"🔁 Updated ContextDefinitionId on existing ESDCD → {record_id}")
            return record_id
        else:
            print(f"❌ Failed to update ESDCD: {patch_resp.status_code} - {patch_resp.text}")
            return None

    print("➕ Creating ExpressionSetDefinitionContextDefinition")
    return create_record(obj_name, record, access_token, instance_url, api_version)


# === REST: PATCH blob ===
import base64

def upload_blob_via_patch(record_id, blob_path, access_token, instance_url, api_version):
    # Build the endpoint for the record (omitting the /ConstraintModel sub-path)
    url = f"{instance_url}/services/data/v{api_version}/sobjects/ExpressionSetDefinitionVersion/{record_id}"

    # Read blob as binary and base64 encode it
    with open(blob_path, "rb") as f:
        blob_data = f.read()
    encoded_blob = base64.b64encode(blob_data).decode("utf-8")
    # Prepare payload; the ConstraintModel field expects a base64 string.
    payload = {
        "ConstraintModel": encoded_blob
    }
    # Use PATCH to update the record
    resp = requests.patch(url, headers=headers, json=payload)
    if resp.status_code == 204:
        print(f"📦 Uploaded blob via PATCH → {record_id}")
    else:
        print(f"⚠️ Blob upload failed → {record_id}: {resp.status_code} - {resp.text}")

# === MAIN ===
def main():
    args = parse_args()
    data_dir = args.data_dir
    dataset_dirs = args.dataset_dir
    target_alias = args.target_org
    blob_dir = os.path.join(data_dir, "blobs")

    global access_token, instance_url, api_version, headers
    access_token, instance_url = get_auth(target_alias)
    api_version = get_latest_api_version(instance_url) # e.g., '66.0'
    print(f"API Version is: {api_version}")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Load all input data
    esdv = read_csv("ExpressionSetDefinitionVersion.csv", data_dir)[0]
    esdcd = read_csv("ExpressionSetDefinitionContextDefinition.csv", data_dir)[0]
    ess = read_csv("ExpressionSet.csv", data_dir)[0]

    esc_list = []
    for dataset_dir in dataset_dirs:
        dataset_path = os.path.join(dataset_dir, "ExpressionSetConstraintObj.csv")
        if os.path.exists(dataset_path):
            esc_list = read_csv_optional(dataset_path)
            break
    if not esc_list:
        esc_list = read_csv("ExpressionSetConstraintObj.csv", data_dir)

    # === Insert ExpressionSet
    ess.pop("Id", None)
    #ess_id = create_record("ExpressionSet", ess, access_token, instance_url, api_version)
    ess_id = upsert_expression_set(ess, access_token, instance_url, api_version)
    if not ess_id:
        print("❌ Could not create or update ExpressionSet. Aborting.")
        return
    
    # Resolve ExpressionSetDefinitionVersion ID by DeveloperName
    devname = esdv["DeveloperName"]
    query_url = f"{instance_url}/services/data/v{api_version}/query"
    headers = { "Authorization": f"Bearer {access_token}" }
    q = f"SELECT Id FROM ExpressionSetDefinitionVersion WHERE DeveloperName = '{devname}'"
    resp = requests.get(query_url, headers=headers, params={"q": q})

    if resp.status_code != 200 or not resp.json().get("records"):
        print(f"❌ Could not find ExpressionSetDefinitionVersion for {devname}")
        return
    esdv_id = resp.json()["records"][0]["Id"]

    # === Insert ExpressionSetDefinitionContextDefinition
    apiname = ess["ApiName"]
    cd_apiname = esdcd.get("ContextDefinitionApiName", "").strip()
    if not cd_apiname:
        print("❌ Invalid ExpressionSetDefinitionContextDefinition: missing ContextDefinitionApiName.")
        print("⚠️ Please ensure your CML Expression Set is using an extended custom Context Definition.")
        return
    
    esdcd.pop("ContextDefinitionApiName", None)
    esdcd.pop("ExpressionSetApiName", None)
    # Resolve ContextDefinition ID by DeveloperName
    q = f"SELECT Id FROM ContextDefinition WHERE DeveloperName = '{cd_apiname}'"
    resp = requests.get(query_url, headers=headers, params={"q": q})

    if resp.status_code != 200 or not resp.json().get("records"):
        print(f"❌ Could not find ContextDefinition for {cd_apiname}")
        return
    cd_id = resp.json()["records"][0]["Id"]
    esdcd["ContextDefinitionId"] = cd_id
    
    # Resolve ExpressionSetDefinition ID by DeveloperName
    q = f"SELECT Id FROM ExpressionSetDefinition WHERE DeveloperName = '{apiname}'"
    resp = requests.get(query_url, headers=headers, params={"q": q})

    if resp.status_code != 200 or not resp.json().get("records"):
        print(f"❌ Could not find ExpressionSetDefinition for {apiname}")
        return
    esd_id = resp.json()["records"][0]["Id"]
    esdcd["ExpressionSetDefinitionId"] = esd_id
	
    #create_record("ExpressionSetDefinitionContextDefinition", esdcd, access_token, instance_url, api_version)
    upsert_esdcd(esdcd, access_token, instance_url, api_version)

    # === Build lookup maps for ReferenceObjectId resolution ===
    print("🔁 Building legacy ID to Unique Key (UK) maps...")

    legacy_to_uk = {}
    product_names = set()
    classification_names = set()
    prc_parent_names = set()

    # Product2
    product2_rows = []
    if dataset_dirs:
        for dataset_dir in dataset_dirs:
            dataset_path = os.path.join(dataset_dir, "Product2.csv")
            if os.path.exists(dataset_path):
                product2_rows = read_csv_optional(dataset_path)
                break
    if not product2_rows:
        product2_rows = read_csv("Product2.csv", data_dir)

    for row in product2_rows:
        legacy_id = row.get("Id", "")
        name = row.get("Name", "")
        if name:
            product_names.add(name)
        if legacy_id:
            legacy_to_uk[legacy_id] = name  # UK for Product2 is just Name

    # ProductClassification
    classification_rows = []
    if dataset_dirs:
        for dataset_dir in dataset_dirs:
            dataset_path = os.path.join(dataset_dir, "ProductClassification.csv")
            if os.path.exists(dataset_path):
                classification_rows = read_csv_optional(dataset_path)
                break
    if not classification_rows and os.path.exists(os.path.join(data_dir, "ProductClassification.csv")):
        classification_rows = read_csv("ProductClassification.csv", data_dir)

    for row in classification_rows:
        legacy_id = row.get("Id", "")
        name = row.get("Name", "")
        if name:
            classification_names.add(name)
        if legacy_id:
            legacy_to_uk[legacy_id] = name  # UK for Classification is just Name

    # ProductRelatedComponent
    prc_rows = []
    if dataset_dirs:
        for dataset_dir in dataset_dirs:
            dataset_path = os.path.join(dataset_dir, "ProductRelatedComponent.csv")
            if os.path.exists(dataset_path):
                prc_rows = read_csv_optional(dataset_path)
                break
    if not prc_rows:
        prc_rows = read_csv("ProductRelatedComponent.csv", data_dir)

    for row in prc_rows:
        legacy_id = row.get("Id", "")
        name = row.get("Name", "")
        if legacy_id and row.get("ParentProduct.Name"):
            uk = (
                row["ParentProduct.Name"] + "|" +
                (row.get("ChildProduct.Name") or "") + "|" +
                (row.get("ChildProductClassification.Name") or "") + "|" +
                (row.get("ProductRelationshipType.Name") or "") + "|" +
                (row.get("Sequence") or "")
            )
            prc_parent_names.add(row["ParentProduct.Name"])
            legacy_to_uk[legacy_id] = uk
        if name:
            prc_parent_names.add(name)

    print("📡 Querying target org for new IDs...")

    headers = {"Authorization": f"Bearer {access_token}"}
    query_url = f"{instance_url}/services/data/v{api_version}/query"

    uk_to_targetId_prod = resolve_name_map(instance_url, api_version, access_token, "Product2", product_names)

    uk_to_targetId_class = resolve_name_map(instance_url, api_version, access_token, "ProductClassification", classification_names)

    uk_to_targetId_prc = {}
    if prc_parent_names:
        prc_filter = ",".join(f"'{n}'" for n in prc_parent_names)
        q3 = f"""
        SELECT Id,
            Name,
            ParentProduct.Name,
            ChildProduct.Name,
            ChildProductClassification.Name,
            ProductRelationshipType.Name, Sequence
        FROM ProductRelatedComponent
        WHERE ParentProduct.Name IN ({prc_filter}) OR Name IN ({prc_filter})
        """
        resp3 = requests.get(query_url, headers=headers, params={"q": q3})
        if resp3.status_code == 200:
            uk_to_targetId_prc = {
                (
                    r["ParentProduct"]["Name"] + "|" +
                    (r["ChildProduct"]["Name"] if r.get("ChildProduct") else "") + "|" +
                    (r["ChildProductClassification"]["Name"] if r.get("ChildProductClassification") else "") + "|" +
                    (r["ProductRelationshipType"]["Name"] if r.get("ProductRelationshipType") else "") + "|" +
                    (str(r["Sequence"]) if r.get("Sequence") is not None else "")
                ): r["Id"]
                for r in resp3.json().get("records", [])
                if r.get("ParentProduct")
            }
        else:
            print(f"⚠️ Failed to query ProductRelatedComponent: {resp3.status_code} - {resp3.text}")

    prc_name_to_id = resolve_name_map(instance_url, api_version, access_token, "ProductRelatedComponent", prc_parent_names)

    print("🔁 Maps ready. Resolving ReferenceObjectIds...")


     # === Insert ExpressionSetConstraintObj
    print("📥 Importing ExpressionSetConstraintObj records...")

    # Step 1: Query all current ESC objects for the ExpressionSet
    esc_query = f"SELECT Id FROM ExpressionSetConstraintObj WHERE ExpressionSetId = '{ess_id}'"
    resp = requests.get(query_url, headers=headers, params={"q": esc_query})
    existing_esc_ids = [r["Id"] for r in resp.json().get("records", [])]

    import_failed = False
    new_count = 0

    for row in esc_list:
        row.pop("Id", None)
        row.pop("ExpressionSet.ApiName", None)
        row.pop("ExpressionSet.Name", None)
        row.pop("ReferenceObject.Name", None)
        row.pop("ReferenceObject.Type", None)
        row.pop("Name", None)
        for key in list(row.keys()):
            if key.startswith("$$"):
                row.pop(key, None)
            if "." in key:
                row.pop(key, None)
        row["ExpressionSetId"] = ess_id

        ref_id = row.get("ReferenceObjectId", "").strip()
        ref_name = row.get("ReferenceObject.Name", "").strip()
        ref_type = row.get("ReferenceObject.Type", "").strip()
        tag_type = row.get("ConstraintModelTagType", "").strip()
        resolved_id = None
        uk = legacy_to_uk.get(ref_id)

        if ref_id:
            if ref_id.startswith("01t"):
                resolved_id = uk_to_targetId_prod.get(uk)
            elif ref_id.startswith("11B") and uk_to_targetId_class:
                resolved_id = uk_to_targetId_class.get(uk)
            elif ref_id.startswith("0dS"):
                resolved_id = uk_to_targetId_prc.get(uk)
        elif ref_name:
            if ref_type == "ProductRelatedComponent" or tag_type.lower() == "port":
                resolved_id = prc_name_to_id.get(ref_name)
            elif ref_type == "ProductClassification":
                resolved_id = uk_to_targetId_class.get(ref_name)
            elif ref_type == "Product2":
                resolved_id = uk_to_targetId_prod.get(ref_name)
            else:
                resolved_id = uk_to_targetId_class.get(ref_name) or uk_to_targetId_prod.get(ref_name)

        if resolved_id:
            row["ReferenceObjectId"] = resolved_id
            if not create_record("ExpressionSetConstraintObj", row, access_token, instance_url, api_version):
                import_failed = True
            else:
                new_count += 1
        else:
            print(f"⚠️ Could not resolve ReferenceObjectId: {ref_id} → UK: {uk}")
            import_failed = True

    print(f"📊 {new_count} new ExpressionSetConstraintObj records created.")

    # Step 2: Decide whether to delete the old records
    if not import_failed:
        print(f"🗑️ Deleting {len(existing_esc_ids)} old ExpressionSetConstraintObj records...")
        for eid in existing_esc_ids:
            del_url = f"{instance_url}/services/data/v{api_version}/sobjects/ExpressionSetConstraintObj/{eid}"
            del_resp = requests.delete(del_url, headers=headers)
            if del_resp.status_code not in [200, 204]:
                print(f"⚠️ Failed to delete {eid}: {del_resp.status_code} - {del_resp.text}")
        print("✅ Old records deleted.")
    else:
        print("⛔ Import encountered errors. Skipping deletion of existing ExpressionSetConstraintObj records.")
        print("⚠️ Warning: Target org now contains a mix of old and new constraints. Manual cleanup may be needed.")
           

    # === Upload Blob
    version = esdv.get("VersionNumber")
    blob_file = os.path.join(blob_dir, f"ESDV_{devname.replace('_V' + version, '')}_V{version}.ffxblob")
    if os.path.exists(blob_file):
        upload_blob_via_patch(esdv_id, blob_file, access_token, instance_url, api_version)
    else:
        print(f"⚠️ Blob file missing: {blob_file}")

if __name__ == "__main__":
    main()
