---
name: salesforce-rlm-homeservices-demo-products
description: Creates Salesforce ARM/RLM demo product records for a Home Services demo org. Researches a target company website, proposes 5-10 products with monthly pricing (including at least one bundle), displays them in a canvas table for user review, then creates all Salesforce records in the correct order: catalog, category, billing schedules, static resource images, products, category assignments, selling model options, and price book entries. Use when the user wants to seed demo data, create product catalog records, or set up a Home Services demo flow in a Salesforce RLM/ARM org.
---

# Salesforce RLM Home Services Demo — Product Creator

> **Skill version: 2026-07-24**
>
> **SOURCE OF TRUTH — READ THIS FIRST.** This skill is distributed inside each demo project. Always run the copy that lives **inside the currently open project folder** (relative `./SKILL.md`, with `./sf-objects-reference.md` and `./scripts/`). If you were invoked from a globally/personally installed copy (`~/.cursor/skills/…`, `~/.claude/skills/…`) or any path outside this project, **discard it and re-read the local project copy**, which is always the authoritative, most up-to-date version. Never mix instructions between a global copy and the local one.

Automates end-to-end creation of demo product catalog data in a Salesforce ARM/RLM (Agentforce Revenue Management) Home Services demo org. This is NOT Salesforce CPQ/Steelbrick — all objects are native RLM.

## Prerequisites
- Salesforce CLI (`sf`) installed
- Run all local scripts from the project root (they reference `scripts/…` relatively)
- **Environment branch is by tool availability, not model name.** If `GenerateImage` and the canvas tooling are available (Cursor — any model: Opus, Sonnet, GPT, etc.), follow the "Cursor" steps. If they are not (Claude Code CLI), follow the "Claude" steps. The model identity is irrelevant; only tool availability decides.

---

## Phase 1 — Research

Browse the user-provided company website URL. Identify **5–10 products or services** to represent as Salesforce demo products.

Rules:
- Assign a realistic **monthly recurring price** to each
- At least one product must be a **bundle**: a parent service with 2–3 optional add-on components priced separately (additive cost, not included in parent price). Example: "Monthly Pest Control" as parent; "Mosquito Treatment Add-on" and "Rodent Control Add-on" as optional children
- Generate a concise **Product Code** using format `HS-KEYWORD-TYPE` (e.g., `HS-PEST-MON`, `HS-MOSQ-ADD`)
- Write a 1–2 sentence **Product Description** for each

Produce an internal product list with: Name, Code, Type (Standalone / Bundle Parent / Bundle Add-on), Monthly Price, parent bundle reference (for add-ons), Description.

---

## Phase 2 — Propose & Confirm

**Image generation:**
- **Cursor**: Run `GenerateImage` for every product using this prompt style:
  `"flat vector illustration of [service name], clean white background, professional marketing style, no text"`
  > **Image path:** `GenerateImage` ignores any subdirectory you request and writes the file to the Cursor project assets directory, returning an **absolute path** (e.g., `/Users/<you>/.cursor/projects/<workspace-slug>/assets/<Filename>.png`). **Capture the exact absolute path it returns for each product** and use that path verbatim when calling the upload script in Phase 5. Do not assume the image is under `assets/images/`.
- **Claude**: Skip image generation. Use `HS_Placeholder` as the resource name for all products. Inform the user that image upload requires Cursor.

**Image embedding for canvas — SKIP (performance):**
> **Do NOT embed product images in the canvas.** Encoding 9+ images as Base64 data URIs produces a 50 KB+ canvas file that is slow to write and slow to render. Images are only needed for the Salesforce Static Resource upload in Phase 5 — they do not need to appear in the proposal canvas.

**Canvas table (Cursor):**
Read the canvas skill and render a `homeservices-product-proposal.canvas.tsx` showing all proposed products using `Card` / `Grid` layout with columns: Product Name, Code, Type, Monthly Price, and Description. Bundle add-ons should be visually grouped under their parent (e.g., left border accent and indented card). Do **not** include `<img>` tags or Base64 image data in the canvas file. (Claude: present the proposal as a markdown table instead.)

**User confirmation — REQUIRED before proceeding:**
After creating the canvas, explicitly ask the user:

> "I've created the product proposal canvas. Please review the proposed products — do they look good, or would you like to adjust any names, prices, descriptions, or add/remove products? Reply **'looks good'** or describe changes and I'll update the proposal before proceeding."

**Do not move to Phase 3 until the user explicitly confirms.**

---

## Phase 3 — Org Authentication & ID Pre-fetch

**Always ask the user for the org username** — never assume a default org is authenticated. Prompt:

> "Which Salesforce org should I load this data into? Please provide the username (e.g., `user@example.com`) and I'll open a browser window for you to authenticate."

Then authenticate:
```bash
sf org login web \
  --instance-url https://login.salesforce.com \
  --alias "HomeServices-Demo" \
  --set-default
```

> **Note:** The browser login window will open automatically. The user must sign in within ~90 seconds. After successful login, the CLI prints the authenticated username — confirm it matches what the user provided before proceeding.

Run and display org info, then ask the user to confirm it is the correct target org:
```bash
sf org display --json
```

Pre-fetch all shared record IDs (run once — reuse throughout Phase 5):
```bash
sf data query --query "SELECT Id FROM TaxPolicy WHERE Name='Default Tax Policy'" --json
sf data query --query "SELECT Id FROM ProrationPolicy WHERE Name='Default Proration Policy'" --json
sf data query --query "SELECT Id FROM ProductSellingModel WHERE Name='Term Monthly'" --json
sf data query --query "SELECT Id FROM Pricebook2 WHERE IsStandard=true" --json
sf data query --query "SELECT Id FROM ProductRelationshipType WHERE Name='Bundle to Bundle Component Relationship'" --json
```

Store: `$TAX_POLICY_ID`, `$PRORATION_POLICY_ID`, `$TERM_MONTHLY_ID`, `$STANDARD_PB_ID`, `$BUNDLE_REL_TYPE_ID`

> If any query returns zero records, stop and inform the user. These records are required for product creation. The org may need setup before proceeding.

> **Billing Schedules are always created (Phase 4c) — never ask the user whether to skip them, and never skip.**

> **Sandbox/network note:** data-writing `sf` commands and REST calls require network access to Salesforce. If your environment sandboxes commands with a restricted network allowlist, run these commands with full network access; otherwise they can fail silently with empty output.

---

## Phase 4 — One-Time Setup

All steps are idempotent — query first, create only if not found.

### Catalog
```bash
sf data query --query "SELECT Id FROM ProductCatalog WHERE Name='<CompanyName> Catalog'" --json
# If not found:
sf data create record --sobject ProductCatalog \
  --values "Name='<CompanyName> Catalog'"
```
> **Note:** `ProductCatalog` does **not** have an `IsActive` field — omit it.

Store: `$CATALOG_ID`

### Category
```bash
sf data create record --sobject ProductCategory \
  --values "Name='Offerings' CatalogId='$CATALOG_ID'"
```
> **Note:** `ProductCategory` does **not** have an `IsActive` field — omit it.

Store: `$CATEGORY_ID`

### Billing Schedules (ALWAYS create — never skip)

Run the idempotent billing setup script. It creates (or reuses) the billing policy, treatment, and 12 milestone items, then activates all of them in the correct order (items → treatment → policy):

```bash
python3 scripts/setup-milestone-billing.py
```

The script prints `BILLING_POLICY_ID=<id>` on its last line. The Phase 5 product script also looks the policy up by name, so you do not need to copy the ID manually — but capture it if you want to confirm.

> **Why a script (do NOT hand-write these `sf data create` calls):** the billing objects require non-obvious fields that the API rejects otherwise. See [sf-objects-reference.md](sf-objects-reference.md) for the full field list. Key gotchas: `BillingPolicy` must be inserted as `Status='Draft'` (cannot insert Active) with `BillingTreatmentSelection='Default'`; `BillingTreatmentItem` uses `Percentage` (not `Percent`), requires `BillingType='None'` for milestone billing, and rejects `Type='Remainder'` (all 12 items are `Percentage`, summing to 100).

---

## Phase 5 — Per-Product Creation (Python REST API)

> **Critical implementation note:** Do NOT use `sf data create record --body` for product records — the `--body` flag does not exist in SF CLI versions prior to 2.130. Do NOT use `--values` for descriptions (quoting issues). Instead, use the **Python REST API approach** for all product creation. This is more reliable, handles large payloads, and is idempotent.

Write a single Python script (`scripts/create_<company>_products.py`) that runs the full sequence for all products. Use the template below.

### Step 1 — Upload Image as Static Resource

Use `scripts/upload-static-resource.sh` for each product image, passing the **absolute path returned by `GenerateImage`** (see Phase 2) — not an `assets/images/` guess:

```bash
bash scripts/upload-static-resource.sh "<absoluteImagePathFromGenerateImage>" "<sanitizedResourceName>"
```

The script is REST-based and idempotent (skips resources that already exist); no SFDX project scaffold is required.

**Claude users:** set `RESOURCE_NAME=HS_Placeholder` and skip this step.

### Steps 2–5 — Python Script Template

```python
#!/usr/bin/env python3
"""
Create all <Company> Home Services demo products in Salesforce via REST API.
Idempotent: queries for existing records before creating.
"""

import json, subprocess, sys, urllib.request, urllib.error, urllib.parse

# ── Shared IDs (fill in from Phase 3 pre-fetch) ─────────────────────────────
TAX_POLICY_ID        = "<from pre-fetch>"
PRORATION_POLICY_ID  = "<from pre-fetch>"
TERM_MONTHLY_ID      = "<from pre-fetch>"
STANDARD_PB_ID       = "<from pre-fetch>"
CATALOG_ID           = "<from Phase 4>"
CATEGORY_ID          = "<from Phase 4>"
BUNDLE_REL_TYPE_ID   = "<from pre-fetch>"   # "Bundle to Bundle Component Relationship"
BILLING_POLICY_NAME  = "Monthly Service - Home Services"  # always set (billing is mandatory)
BUNDLE_CODE          = "<HS-XXX-BDL>"       # ProductCode of the bundle parent

# ── Product definitions ──────────────────────────────────────────────────────
PRODUCTS = [
    {
        "name": "...",
        "code": "HS-XXX-MON",
        "type": "standalone",   # "standalone" | "bundle" | "addon"
        "price": 299,
        "resource": "HS_XXX_MON",
        "description": "...",
        # "parent": "HS-XXX-BDL",  # add-ons only
    },
    # ... repeat for all products
]

# ── Auth ─────────────────────────────────────────────────────────────────────
def get_org_info():
    result = subprocess.run(["sf", "org", "display", "--json"],
                            capture_output=True, text=True)
    data = json.loads(result.stdout)["result"]
    return data["accessToken"], data["instanceUrl"], data.get("apiVersion", "66.0")

ACCESS_TOKEN, INSTANCE_URL, API_VERSION = get_org_info()
BASE_URL = f"{INSTANCE_URL}/services/data/v{API_VERSION}"

# ── REST helpers ─────────────────────────────────────────────────────────────
def sf_query(soql):
    url = f"{BASE_URL}/query?q={urllib.parse.quote(soql)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read()).get("records", [])

def sf_post(path, body):
    url = f"{BASE_URL}{path}"
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read())
            if not result.get("success"):
                print(f"  ERROR: {result}", file=sys.stderr); sys.exit(1)
            return result["id"]
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()}", file=sys.stderr); sys.exit(1)

# Billing is mandatory — resolve the policy ID by name (created in Phase 4c)
_bp = sf_query(f"SELECT Id FROM BillingPolicy WHERE Name='{BILLING_POLICY_NAME}'")
if not _bp:
    print("ERROR: Billing policy not found. Run scripts/setup-milestone-billing.py first.", file=sys.stderr)
    sys.exit(1)
BILLING_POLICY_ID = _bp[0]["Id"]

# ── Per-product sequence (Steps 2–5) ────────────────────────────────────────
product_ids = {}

for p in PRODUCTS:
    print(f"\n[{p['code']}] {p['name']}")

    # Step 2 — Product2 (idempotent)
    existing = sf_query(f"SELECT Id FROM Product2 WHERE ProductCode='{p['code']}'")
    if existing:
        product_id = existing[0]["Id"]
        print(f"  Product2: {product_id} (existing)")
    else:
        display_url = f"/resource/{p['resource']}"
        payload = {
            "Name": p["name"], "ProductCode": p["code"],
            "Description": p["description"],
            "IsActive": True, "IsAssetizable": True,
            "CurrencyIsoCode": "USD",
            "DisplayUrl": display_url,
            "TaxPolicyId": TAX_POLICY_ID,
            "BillingPolicyId": BILLING_POLICY_ID,   # billing is mandatory
        }
        if p["type"] == "bundle":
            payload["Type"] = "Bundle"
            payload["ConfigureDuringSale"] = "Allowed"
        product_id = sf_post("/sobjects/Product2", payload)
        print(f"  Product2: {product_id} (created)")
    product_ids[p["code"]] = product_id

    # Step 3 — Category assignment (idempotent)
    ec = sf_query(f"SELECT Id FROM ProductCategoryProduct WHERE ProductId='{product_id}' AND ProductCategoryId='{CATEGORY_ID}'")
    if ec:
        print(f"  CategoryProduct: {ec[0]['Id']} (existing)")
    else:
        cid = sf_post("/sobjects/ProductCategoryProduct",
                      {"ProductId": product_id, "ProductCategoryId": CATEGORY_ID})
        print(f"  CategoryProduct: {cid} (created)")

    # Step 4 — Selling model option (idempotent)
    # Field is Product2Id, NOT ProductId
    es = sf_query(f"SELECT Id FROM ProductSellingModelOption WHERE Product2Id='{product_id}' AND ProductSellingModelId='{TERM_MONTHLY_ID}'")
    if es:
        print(f"  SellingModelOption: {es[0]['Id']} (existing)")
    else:
        sid = sf_post("/sobjects/ProductSellingModelOption", {
            "Product2Id": product_id,          # NOTE: Product2Id, not ProductId
            "ProductSellingModelId": TERM_MONTHLY_ID,
            "ProrationPolicyId": PRORATION_POLICY_ID,
            "IsDefault": True,                 # required so pricing resolves
        })
        print(f"  SellingModelOption: {sid} (created)")

    # Step 5 — Price book entry (idempotent)
    ep = sf_query(f"SELECT Id FROM PricebookEntry WHERE Product2Id='{product_id}' AND Pricebook2Id='{STANDARD_PB_ID}'")
    if ep:
        print(f"  PricebookEntry: {ep[0]['Id']} (existing)")
    else:
        pid = sf_post("/sobjects/PricebookEntry", {
            "Product2Id": product_id, "Pricebook2Id": STANDARD_PB_ID,
            "UnitPrice": p["price"], "IsActive": True,
            "ProductSellingModelId": TERM_MONTHLY_ID,
        })
        print(f"  PricebookEntry: {pid} (created)  ${p['price']}/mo")

# ── Phase 5b — Bundle setup ──────────────────────────────────────────────────
bundle_parent_id = product_ids[BUNDLE_CODE]
addons = [p for p in PRODUCTS if p["type"] == "addon"]

eg = sf_query(f"SELECT Id FROM ProductComponentGroup WHERE ParentProductId='{bundle_parent_id}' AND Name='Optional Add-ons'")
if eg:
    group_id = eg[0]["Id"]
    print(f"  ComponentGroup: {group_id} (existing)")
else:
    group_id = sf_post("/sobjects/ProductComponentGroup", {
        "Name": "Optional Add-ons",
        "ParentProductId": bundle_parent_id,
        "MinBundleComponents": 0,               # NOTE: MinBundleComponents, not MinQty
        "MaxBundleComponents": len(addons),      # NOTE: MaxBundleComponents, not MaxQty
        "Sequence": 1,
    })
    print(f"  ComponentGroup: {group_id} (created)")

for i, addon in enumerate(addons, start=1):
    child_id = product_ids[addon["code"]]
    el = sf_query(f"SELECT Id FROM ProductRelatedComponent WHERE ProductComponentGroupId='{group_id}' AND ChildProductId='{child_id}'")
    if el:
        print(f"  RelatedComponent [{addon['code']}]: {el[0]['Id']} (existing)")
    else:
        lid = sf_post("/sobjects/ProductRelatedComponent", {
            "ProductComponentGroupId": group_id,    # NOTE: ProductComponentGroupId, not ParentProductComponentGroupId
            "ParentProductId": bundle_parent_id,    # NOTE: required — include the parent product ID
            "ChildProductId": child_id,
            "ProductRelationshipTypeId": BUNDLE_REL_TYPE_ID,  # NOTE: required — pre-fetched in Phase 3
            "IsDefaultComponent": False,            # always False — add-ons are optional, not pre-selected (NOTE: IsDefaultComponent, not IsDefault)
            "DoesBundlePriceIncludeChild": False,   # always False — child priced separately (defaults True if omitted)
            "Quantity": 1,
            "Sequence": i,
        })
        print(f"  RelatedComponent [{addon['code']}]: {lid} (created)")
```

---

## Completion

After all records are created, display a summary to the user:
- Catalog and category created
- Billing Schedule status (created or reused — always present)
- List of all products created with their Salesforce record IDs
- Bundle structure confirmation (parent → component group → children)
- Any skipped steps (e.g., images skipped in Claude)

For detailed field-level reference on all objects used, see [sf-objects-reference.md](sf-objects-reference.md).

---

## Known Field Corrections (learned from live runs)

These are confirmed field name differences between the skill's initial documentation and the actual Salesforce API — apply these everywhere:

| Object | Wrong (old) | Correct |
|---|---|---|
| `ProductCatalog` | `IsActive` | *(field does not exist — omit)* |
| `ProductCategory` | `IsActive` | *(field does not exist — omit)* |
| `ProductSellingModelOption` | `ProductId` | `Product2Id` |
| `ProductComponentGroup` | `MinQty` | `MinBundleComponents` |
| `ProductComponentGroup` | `MaxQty` | `MaxBundleComponents` |
| `ProductRelatedComponent` | `ParentProductComponentGroupId` | `ProductComponentGroupId` |
| `ProductRelatedComponent` | `IsDefault` | `IsDefaultComponent` ← always set to `False` |
| `ProductRelatedComponent` | *(missing)* | `DoesBundlePriceIncludeChild` ← always set to `False` (defaults to `True` if omitted) |
| `ProductRelatedComponent` | *(missing)* | `ParentProductId` ← required |
| `ProductRelatedComponent` | *(missing)* | `ProductRelationshipTypeId` ← required |
| `ProductRelatedComponent` | `ParentProductRole` / `ChildProductRole` | *(read-only — auto-set by system, do not pass)* |
| `Product2` | custom image-resource-name field | `DisplayUrl` ← use `/resource/<sanitizedResourceName>` as the single image source |
| `BillingPolicy` | *(only `Name`)* | + `Status='Draft'` on insert, `BillingTreatmentSelection='Default'`; activate later with `DefaultBillingTreatmentId` + `Status='Active'` |
| `BillingTreatment` | *(only `Name`+`BillingPolicyId`)* | + `Status='Draft'`, `ExcludeFromBilling='No'`, `IsMilestoneBilling=true`, `CanChangeBillingFrequency=false` |
| `BillingTreatmentItem` | `Percent`; `Type='Remainder'` (month 12) | `Percentage`; all 12 `Type='Percentage'` summing to 100; `BillingType='None'`, `Sequencing='None'`, `Controller='None'`, `Handling0Amount='None'`, `MilestoneType='Event'`, `Status` |
| Billing activation | *(not documented)* | order: items `Active` → treatment `Active` → policy (`DefaultBillingTreatmentId` + `Active`) |
| `sf data create record` | `--body <file>` | *(flag does not exist before CLI v2.130 — use Python REST API)* |
| StaticResource upload | `sf project deploy start --metadata` | REST POST to `sobjects/StaticResource` (see `scripts/upload-static-resource.sh`) — no SFDX scaffold needed |
