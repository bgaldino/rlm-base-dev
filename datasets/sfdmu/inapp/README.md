# In-App Learning Navigation — SFDMU Data Plan (DRAFT)

> **Status: DRAFT / design preview.** SFDMU v5 conversion of the Industries In-App
> Framework's legacy CumulusCI dataset
> (`Industries-In-App-Framework/datasets/rlm/rlm.dataset.sql`). `export.json` is
> complete; `Page__c.csv` is fully converted (10 rows); other CSVs are verified
> samples until the conversion script runs. Loaded by the proposed `inapp` feature
> (`unpackaged/post_inapp` + `project__custom__inapp`).

## What this loads

Drives the **Learning Home** in-app navigation: a data-defined home page and
per-capability detail pages (PCM, Pricing, Billing, DRO, Rating, Contracts, Usage)
built from Pages → Sections → Blocks, with `DynamicLink__c` resolving in-app popups,
detail links, and external resources. All six objects are framework-owned custom
objects shipped in `unpackaged/post_inapp`; the plan inserts into **no** RLM/QuantumBit
object, so it cannot collide with the product/pricing datasets.

## externalId scheme — natural composite keys (no synthetic field)

The data already carries usable keys, so **no `External_Id__c` field is added**. Five
of six objects key on their unique `Name`; only the junction needs a true composite.

| # | Object | Operation | externalId | Records | Key type |
|---|--------|-----------|------------|---------|----------|
| 1 | `Icon__c`         | Upsert | `Name` | 22  | natural — direct, unique 22/22 |
| 2 | `Page__c`         | Upsert | `Name` | 10  | natural — direct, unique 10/10 |
| 3 | `Section__c`      | Upsert | `Name` | 72  | natural — direct, unique 72/72 |
| 4 | `DynamicLink__c`  | Upsert | `Name` | 51  | natural — direct, unique 51/51 (`Identity__c` rejected: 4 blanks) |
| 5 | `Block__c`        | Upsert | `Name` | 126 | natural — direct, unique 126/126 **after dead-row scrub** |
| 6 | `SectionBlock__c` | **Insert + deleteOldData** | `Section__r.Name;Block__r.Name;Order_Sequence__c` | 120 | **composite** — 2 parent traversals + 1 direct field |

Total: **401 records** (405 source − 2 dead blocks − 2 orphan junction rows).

### Why this is SFDMU v5-compliant
- **Bug 1 (all-multi-hop externalId fails):** the junction key includes the **direct**
  field `Order_Sequence__c`, so it is not all-traversal. ✅
- **Bug 3/5 (relationship-traversal externalId never matches on Upsert → duplicates):**
  **confirmed on a live load** — the composite-traversal externalId does NOT match on
  re-Upsert, so `SectionBlock__c` uses **`operation: Insert` + `deleteOldData: true`** (the
  CLAUDE.md Bug 5 fix). Verified idempotent: three consecutive loads hold the junction at
  120 (an Upsert junction doubled to 240). Repo precedent for composite-traversal +
  `deleteOldData`: `qb-dro` `FulfillmentWorkspaceItem`.
- The single-`Name`-key parents (Icon/Page/Section/DynamicLink/Block) are idempotent under
  Upsert; only the junction needs `deleteOldData`.
- Each parent traversal references that parent's own externalId (`Name`), so resolution
  is unambiguous — which is **why the dead-block scrub is required** (see below): a
  non-unique `Block.Name` would make `Block__r.Name` ambiguous.

Verified-unique: `Section__r.Name;Block__r.Name` is already unique 120/120; the
`Order_Sequence__c` component is added for Bug-1 compliance and is harmless on this
static data.

## Record-type handling

`Section__c` (5 RTs: `Detail`, `Left_Bottom`, `Left_Top`, `Right`, `Top`) and
`DynamicLink__c` (14 RTs incl. `InAppPopup`, `InAppDetailsPage`, `AppPage`, `WebPage`,
`RecordPage`) carry `RecordTypeId` in the query so SFDMU maps record types **by
DeveloperName**; the CSVs provide a `RecordType.DeveloperName` column (the source
18-char Ids are dropped). All referenced record types ship in `post_inapp`.

## Scrub & remap — applied by `convert_from_legacy.py`

**Key-enabling (required for the composite scheme):**
- **Dropped 2 unreferenced "dead" blocks** so `Block.Name` is unique: `Block__c-73`
  (`Product Catalog Management Top Block`, actually a mislabeled Product Configurator
  block) and `Block__c-50` (`DRO Learning Block 3`, a "TBD" placeholder). Neither is
  referenced by any `SectionBlock__c`, so dropping them changes nothing functionally.
- **Dropped 2 orphan junction rows** `SectionBlock__c-1/-2` (blank Section + Block).

**Data remap → QuantumBit / rlm-base-dev defaults:**
- **Account `Mahesh` → `Infinitech`.** The only record-specific data reference in the
  whole learning dataset was `DynamicLink` `ACC_MAHESH_DYN_LINK` (a `RecordPage` link:
  `Object__c=Account`, `Where='Name=''Mahesh'''`). Remapped to `Name = 'Infinitech'`
  (the QuantumBit primary customer from `scratch_data/Account.csv`); the
  `Identity__c`/`Name` were renamed to `ACC_INFINITECH_DYN_LINK` / `Account Name
  Infinitech` in lockstep.
- **No product-SKU references to remap.** A full scan found the learning content is
  capability-level, not product-level. The product-shaped strings are either generic UI
  copy ("Product Catalog Management") or **`standard__*` app API names**
  (`standard__PriceManagement`, `BillingConsole`, `SalesforceContracts`,
  `UsageManagement`, `RatingManagement`, `IndustriesEpc/Dfo`) — platform app links that
  resolve in any RLM org. These are left intact.
- **15× cross-org images stripped (PENDING re-host — see below).** `Block__c` rich text
  embedded `rlm258learnorg.file.force.com/servlet/rtaImage?eid=…` images. Verified: all 15
  return HTTP 302→login (session-gated to the source org, not 404), so they render broken
  in any other org; the binaries aren't carried by the dataset. The `<img>` tags are
  stripped for now so no broken host ships. **This is the only blocker on opening the PR.**

### Restoring the 15 stripped images — exact landing (do this when the binaries arrive)

The original images live in the source org `rlm258learnorg` (inline images on the 15
`Block__c.Description__c` rich-text fields). Full inventory (Block id, owning record `eid`,
image `refid`, original filename, capability page) is in
`.agents/artifacts/in-app-framework-stripped-images-manifest.md` (regenerable from the
source `rlm.dataset.sql`).

When the 15 binaries are obtained (source-org login or clone):

1. **Image files → `unpackaged/post_inapp/staticresources/`** as a single zip static
   resource: `InAppLearningImages.resource` (zip of the 15 images, named per the manifest,
   e.g. `block-2-revenue-cloud-fundamentals.png`) + `InAppLearningImages.resource-meta.xml`
   (`<contentType>application/zip</contentType>`). One static resource keeps the bundle tidy.
2. **URL rewrite → `convert_from_legacy.py` `scrub_text()`:** flip the image handling from
   *strip* to *rewrite* — replace each `…/servlet/rtaImage?…refid=<R>` with
   `/resource/InAppLearningImages/<mapped-filename>` using a `refid → filename` map (15
   entries, from the manifest). Then re-run the converter to regenerate the CSVs.
3. **Reload** (`cci task run load_inapp_dataset --org <alias>`) and confirm the Learning
   Home renders the images.
4. Open the PR.

No other files change — the images are referenced only inside `Block__c.Description__c`,
which the converter owns.

**Deferred (editorial — not blocking the load):**
- **Wrong-vertical WebPages** `DynamicLink` "Release Notes" → Comms Summer '24 / Energy
  Winter '25; should point at Revenue Cloud release notes.
- **4× `dwd…lightning.force.com` + 2× `drive.google.com`** hrefs in rich text — personal/dev-org links to re-point or drop.

## Conversion mechanics (source → this plan)

`convert_from_legacy.py` (in this directory) reads `rlm.dataset.sql` and emits all six
CSVs: (1) translate `RecordTypeId` → `RecordType.DeveloperName` via the source
`*_rt_mapping` tables; (2) rewrite each lookup (a source row id) to the parent's **`Name`**
via the `<rel>__r.Name` column; (3) emit the SFDMU v5 **`$$`** composite-key column for
the junction; (4) lowercase booleans; (5) apply the scrub, Infinitech remap, and the 262
link/label remap (see "262 verification status"). Re-run it to regenerate:

```bash
python datasets/sfdmu/inapp/convert_from_legacy.py [path/to/rlm.dataset.sql]
```

## 262 verification status (content was last authored for 258 / Winter '26)

Verified against `docs/salesforce/262/` — the **838-article Help snapshot**, the
**1388-article Developer Guide (atlas) snapshot**, and `feature-index.md` — per the
canonical `.cursor/skills/revenue-cloud-docs/SKILL.md` (the plugin-cached skill copy is
stale and omits the dev-guide corpus). 262 = Summer '26; 258 = Winter '26.

**Link health:**
- **Developer-guide (atlas) links — 34/36 valid in 262.** Only `asset_lifecycle_overview`
  and `transaction_management_overview` are stale.
- **Help (`ind.*`) links — 42/90 valid; 48 renamed.** The renames are mostly area
  *consolidations*: Transaction Management + Salesforce Contracts → `ind.qocal_*`
  (Quote-Order-Contract-Asset-Lifecycle combined); pricing → `ind.pricing_*`; catalog →
  `ind.product_catalog_*`.

**Applied by `convert_from_legacy.py` (all targets verified to exist in the 262 snapshot):**
- **48 renamed Help article IDs → 262 equivalents** (`HELP_ID_REMAP`). Where 262 reorganized
  deep articles into a consolidated area, the link lands on the capability's 262 page
  (Contracts/Transaction → `ind.qocal_*`, pricing → `ind.pricing_*`, catalog →
  `ind.product_catalog_*`); a precise article is kept where the 262 match is unambiguous.
- **2 stale dev-guide pages → 262** (`asset_lifecycle_overview` /
  `transaction_management_overview` → `quote_and_order_capture_standard_objects`).
- **Release pin `258 → 262`** on every help link (now 15× `release=262`, 0× `258`).
- **"Price Management" → "Salesforce Pricing"** — the 262 capability label, applied to the
  Page record + all **visible** fields (headers/descriptions). Internal record `Name` keys
  keep "Price Management" (not user-visible, avoids a needless externalId cascade); the app
  API name `standard__PriceManagement` is unchanged.
- Version label `Winter'26 Release` → `Summer '26 Release`; 2 wrong-vertical "Release Notes"
  home links → Revenue Cloud 262 release notes.

**Deferred (editorial — not blocking the load, low value for the temporary integration):**
- **3× 258-headline-feature `rn_*` callouts** (`rn_dro_enable_smooth_transfers`,
  `rn_dro_fulfillment_scheduling_with_custom_dates`,
  `rn_transaction_management_ramp_deals_for_groups`) — these are *258's* news; their release
  pins were bumped, but the right 262 move is to swap in 262 headline features from
  `feature-index.md`. Release-notes (`rn_*`) are not in the snapshot, so they can't be
  auto-verified.
- **Release video** (`vidyard …Winter'26`) → the actual Summer '26 launch video (URL not
  derivable from docs).
- **Product umbrella rebrand "Revenue Cloud" → "Agentforce Revenue Management"** — left as-is:
  it's *selective* ("Revenue Cloud Billing" and Trailhead trail proper-nouns persist), so a
  blanket replace would be wrong; this is a redesign-era editorial call.

## CSV column layouts

| Object | Header |
|--------|--------|
| `Icon__c` | `Name,Size__c,Type__c` |
| `Page__c` | `Active__c,Name,Type__c` |
| `Section__c` | `Active__c,Header__c,Name,Sub_Header__c,Video_Link__c,RecordType.DeveloperName,Icon__r.Name,Page__r.Name` |
| `DynamicLink__c` | `App_API_Name__c,Filter_Name__c,Identity__c,Link__c,Name,Object__c,Page_Name__c,Relationship_API_Name__c,Relative_Url__c,Setup_Page__c,Site_Name__c,Text_Value__c,Where_Condition__c,RecordType.DeveloperName,Page__r.Name,Section__r.Name` |
| `Block__c` | `ActionText__c,Active__c,Description__c,Header__c,Name,Note__c,Sub_Header__c,Action__r.Name,Icon__r.Name` |
| `SectionBlock__c` | `$$Section__r.Name$Block__r.Name$Order_Sequence__c,Section__r.Name,Block__r.Name,Order_Sequence__c` |

## Org load — verified working + SFDMU requirements

Deployed + loaded + verified on scratch org `ent-r1` (2026-06-19). The framework's
`SectionBlockController.getSectionsWithBlocksByType` returns fully-resolved sections →
blocks → icons → dynamic links. Four non-obvious requirements were needed to make SFDMU
resolve everything (each surfaced only on a live load):

1. **Lookup fields must be in the query, not just the traversal.** Each lookup needs BOTH
   the `__c` field AND the `__r.Name` traversal in the `export.json` query (e.g.
   `…, Icon__c, Page__c, Icon__r.Name, Page__r.Name`). With only the traversal, SFDMU
   drops the lookup from the insert and the foreign key lands null.
2. **RecordType is matched on a 2-part `DeveloperName;SobjectType` externalId.** A
   `RecordType` object (operation `Readonly`) is declared first in `export.json`, with a
   source `RecordType.csv` (the 19 record types). The default 3-part composite
   (`…;NamespacePrefix;…`) fails because NamespacePrefix is null on unmanaged record types
   (SFDMU's null ≠ the CSV's empty string).
3. **The running user needs record-type visibility.** `RLM_InApp_Learning` includes
   `recordTypeVisibilities` for all 19 record types — without them the insert fails with
   "Record Type ID isn't valid for the user."
4. **Permission-set hygiene:** required fields (`Icon__c.Size__c`, `Page__c.Type__c`) are
   excluded from FLS; the Section layouts' `<platformActionList>` (Chatter `RypplePost`)
   was stripped from `post_inapp` (invalid on scratch orgs).

### Junction idempotency — fixed ✅

The composite-traversal externalId on `SectionBlock__c` does **not** match on re-Upsert
(CLAUDE.md SFDMU Bug 3/5) — a live load proved a re-run doubled the 120 junction rows to 240.
**Fix applied:** `SectionBlock__c` uses **`operation: Insert` + `deleteOldData: true`**, which
wipes the junction and reinserts each run. Verified idempotent on `ent-r1`: three consecutive
loads held it at 120 (total 401, no drift). `deleteOldData` only targets the junction (its
parents are Upsert-idempotent on their `Name` key), and the junction has no inbound references,
so the per-run wipe is safe.

## Run

```bash
# Loaded automatically by prepare_inapp when project__custom__inapp is true.
# Manual (CSV → org):
sf sfdmu run --sourceusername csvfile --targetusername <sf_alias> \
  --path datasets/sfdmu/inapp

# Convention checks (must report 0 errors before merge):
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/inapp
python scripts/ai/check_plan_readme_consistency.py datasets/sfdmu/inapp
```
