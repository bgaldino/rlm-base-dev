# In-App Learning Navigation — SFDMU Data Plan (DRAFT)

> **Status: DRAFT / design preview.** SFDMU v5 conversion of the Industries In-App
> Framework's legacy CumulusCI dataset
> (`Industries-In-App-Framework/datasets/rlm/rlm.dataset.sql`). `export.json` is
> complete; `RLM_Learning_Page__c.csv` is fully converted (10 rows); other CSVs are verified
> samples until the conversion script runs. Loaded by the proposed `inapp` feature
> (`unpackaged/post_inapp` + `project__custom__inapp`).

## What this loads

Drives the **Learning Home** in-app navigation: a data-defined home page and
per-capability detail pages (PCM, Pricing, Billing, DRO, Rating, Contracts, Usage)
built from Pages → Sections → Blocks, with `RLM_Learning_DynamicLink__c` resolving in-app popups,
detail links, and external resources. All six objects are framework-owned custom
objects shipped in `unpackaged/post_inapp`; the plan inserts into **no** RLM/QuantumBit
object, so it cannot collide with the product/pricing datasets.

## externalId scheme — natural composite keys (no synthetic field)

The data already carries usable keys, so **no `External_Id__c` field is added**. Five
of six objects key on their unique `Name`; only the junction needs a true composite.

| # | Object | Operation | externalId | Records | Key type |
|---|--------|-----------|------------|---------|----------|
| 1 | `RLM_Learning_Icon__c`         | Upsert | `Name` | 22  | natural — direct, unique 22/22 |
| 2 | `RLM_Learning_Page__c`         | Upsert | `Name` | 10  | natural — direct, unique 10/10 |
| 3 | `RLM_Learning_Section__c`      | Upsert | `Name` | 72  | natural — direct, unique 72/72 |
| 4 | `RLM_Learning_DynamicLink__c`  | Upsert | `Name` | 51  | natural — direct, unique 51/51 (`RLM_Learning_Identity__c` rejected: 4 blanks) |
| 5 | `RLM_Learning_Block__c`        | Upsert | `Name` | 126 | natural — direct, unique 126/126 **after dead-row scrub** |
| 6 | `RLM_Learning_SectionBlock__c` | **Insert + deleteOldData** | `RLM_Learning_Section__r.Name;RLM_Learning_Block__r.Name;RLM_Learning_Order_Sequence__c` | 120 | **composite** — 2 parent traversals + 1 direct field |

Total: **401 records** (405 source − 2 dead blocks − 2 orphan junction rows).

### Why this is SFDMU v5-compliant
- **Bug 1 (all-multi-hop externalId fails):** the junction key includes the **direct**
  field `RLM_Learning_Order_Sequence__c`, so it is not all-traversal. ✅
- **Bug 3/5 (relationship-traversal externalId never matches on Upsert → duplicates):**
  **confirmed on a live load** — the composite-traversal externalId does NOT match on
  re-Upsert, so `RLM_Learning_SectionBlock__c` uses **`operation: Insert` + `deleteOldData: true`** (the
  CLAUDE.md Bug 5 fix). Verified idempotent: three consecutive loads hold the junction at
  120 (an Upsert junction doubled to 240). Repo precedent for composite-traversal +
  `deleteOldData`: `qb-dro` `FulfillmentWorkspaceItem`.
- The single-`Name`-key parents (Icon/Page/Section/DynamicLink/Block) are idempotent under
  Upsert; only the junction needs `deleteOldData`.
- Each parent traversal references that parent's own externalId (`Name`), so resolution
  is unambiguous — which is **why the dead-block scrub is required** (see below): a
  non-unique `Block.Name` would make `RLM_Learning_Block__r.Name` ambiguous.

Verified-unique: `RLM_Learning_Section__r.Name;RLM_Learning_Block__r.Name` is already unique 120/120; the
`RLM_Learning_Order_Sequence__c` component is added for Bug-1 compliance and is harmless on this
static data.

## Record-type handling

`RLM_Learning_Section__c` (5 RTs: `Detail`, `Left_Bottom`, `Left_Top`, `Right`, `Top`) and
`RLM_Learning_DynamicLink__c` (14 RTs incl. `InAppPopup`, `InAppDetailsPage`, `AppPage`, `WebPage`,
`RecordPage`) carry `RecordTypeId` in the query so SFDMU maps record types **by
DeveloperName**; the CSVs provide a `RecordType.DeveloperName` column (the source
18-char Ids are dropped). All referenced record types ship in `post_inapp`.

## Scrub & remap — applied by `convert_from_legacy.py`

**Key-enabling (required for the composite scheme):**
- **Dropped 2 unreferenced "dead" blocks** so `Block.Name` is unique: `RLM_Learning_Block__c-73`
  (`Product Catalog Management Top Block`, actually a mislabeled Product Configurator
  block) and `RLM_Learning_Block__c-50` (`DRO Learning Block 3`, a "TBD" placeholder). Neither is
  referenced by any `RLM_Learning_SectionBlock__c`, so dropping them changes nothing functionally.
- **Dropped 2 orphan junction rows** `RLM_Learning_SectionBlock__c-1/-2` (blank Section + Block).

**Data remap → QuantumBit / rlm-base-dev defaults:**
- **Account `Mahesh` → `Infinitech`.** The only record-specific data reference in the
  whole learning dataset was `DynamicLink` `ACC_MAHESH_DYN_LINK` (a `RecordPage` link:
  `RLM_Learning_Object__c=Account`, `Where='Name=''Mahesh'''`). Remapped to `Name = 'Infinitech'`
  (the QuantumBit primary customer from `scratch_data/Account.csv`); the
  `RLM_Learning_Identity__c`/`Name` were renamed to `ACC_INFINITECH_DYN_LINK` / `Account Name
  Infinitech` in lockstep.
- **No product-SKU references to remap.** A full scan found the learning content is
  capability-level, not product-level. The product-shaped strings are either generic UI
  copy ("Product Catalog Management") or **`standard__*` app API names**
  (`standard__PriceManagement`, `BillingConsole`, `SalesforceContracts`,
  `UsageManagement`, `RatingManagement`, `IndustriesEpc/Dfo`) — platform app links that
  resolve in any RLM org. These are left intact.
- **15× cross-org images re-hosted (DONE).** `RLM_Learning_Block__c` rich text embedded
  `rlm258learnorg.file.force.com/servlet/rtaImage?eid=…` images, session-gated to the source
  org (HTTP 302→login, not 404), so they render broken anywhere else. The 15 binaries were
  retrieved from a 258-template scratch org and are now **self-hosted** in the
  `InAppLearningImages` static resource; `convert_from_legacy.py` rewrites each `<img src>` to
  `/resource/InAppLearningImages/<block-name-slug>.<ext>`. Verified served (HTTP 200,
  matching content-type) on `ent-r1`.
- **Home announcement updated to Summer '26 (DONE).** The `Home Left Top Block` listed four
  258 features and an "Explore Winter'26 Release Notes" link label. `convert_from_legacy.py`
  (`rewrite_home_relnotes`) swaps the bullets for four 262 marquee features — Product
  Discovery with Constraint Rules (GA), Accelerated Deal Approvals in Slack, Guided Ramp
  Creation with Trial Segments, AI-Supported Bulk Contract Extraction — each verified in
  `docs/salesforce/262/feature-index.md`, and fixes the link label to "Summer '26" (the href
  was already `release=262`).

### Image re-host — how it works

The 15 images are referenced only inside `RLM_Learning_Block__c.RLM_Learning_Description__c`. Full inventory (Block id,
owning record `eid`, image `refid`, original filename, capability page) is in
`.agents/artifacts/in-app-framework-stripped-images-manifest.md`.

- **Files:** `unpackaged/post_inapp/staticresources/InAppLearningImages/` (15 images, one per
  image-bearing block, named `<block-name-slug>.png` — all normalized to PNG; the 3 the source
  served as JPEG were re-encoded) + `InAppLearningImages.resource-meta.xml`
  (`<contentType>application/zip</contentType>`, deployed as a single zip static resource).
- **URL rewrite:** `convert_from_legacy.py` `rewrite_block_images()` matches each block by
  Name-slug to the staged file (dir-scan picks up the on-disk extension) and rewrites the
  dead-host `<img src>` to `/resource/InAppLearningImages/<slug>.png`. The `scrub_text` strip
  remains as a fallback for any unstaged image. Re-running the converter is idempotent.

To refresh an image: replace the file in the static-resource dir, re-run the converter, reload
(`cci task run load_inapp_dataset --org <alias>`).

**262 area-block sweep (DONE).** The Home block + all 8 area "what's new" blocks (DRO, Billing,
Usage, PCM, Pricing, Product Configurator, Salesforce Contracts, Transaction Management) now
read "Summer '26" with verified 262 feature bullets (`rewrite_sibling_relnotes` in
`convert_from_legacy.py`, grounded in `docs/salesforce/262/feature-index.md`, tiers shown). Each
block's area-level "Read More" link (already `release=262`) is preserved; the 258 per-feature
deep links were dropped. App label also aligned to source: "Learning Home" → "Revenue Cloud
Learning Home".

**External-link validation (DONE).** All 144 unique external URLs in the journey were verified
(`ind.*` Help IDs + dev-guide pages cross-checked against the local 262 snapshots; release-notes,
trailhead, YouTube, and the rest live-checked — note help.salesforce.com / developer.salesforce.com
are SPAs that 200 on dead pages, so validity was confirmed by rendered title/content or oembed,
not curl status). Fixed in `convert_from_legacy.py`:
- **2 dead release-notes links** (404 at 262) → browser-verified 262 equivalents (`RN_ID_REMAP`):
  `rn_salesforce_qoc` → `rn_transaction_management`; `rn_rate_management` → `rn_um_usage_management`.
- **1 dead Help slug** `…salesforce_contracts_winter_23.htm` → `ind.qocal_contract_management_essentials.htm`
  (added to `HELP_ID_REMAP`).
- **4 personal demo-org URLs** (`dwd…lightning.force.com`, DNS-dead) → relativized to `/lightning/…`
  (portable in any org; `DEMO_ORG_HOST` strip).
- **1 malformed nav path** `/lightning/lightning/…BillingConsole…` → collapsed to `/lightning/…`.
- **Billing "Dashboard Setup"** link (was a placeholder Drive doc + "To Be Updated") → the 262
  **Billing Operations Console** Help article (`ind.billing_operations_console.htm`) with a grounded
  description.
Validated valid (left as-is): 55 `ind.*` articles, 35 RLM + 3 CLM dev-guide pages, 8 release-notes
area pages, 16 Trailhead modules/trails, 4 YouTube + 1 Vidyard video, ideas/marketing pages.

**DynamicLink Name fixes (DONE).** Two `DynamicLink` record Names (the SFDMU composite key)
corrected via `DL_NAME_REMAP`: stale "Winter '25 Release Notes" → "Summer '26 Release Notes"
(the last "Winter" reference in the dataset) and typo "Relese Notes Summary" → "Release Notes
Summary". Both had 0 lockstep references. **Keyed-rename caveat:** Name-keyed Upsert *inserts*
the new-named record and leaves the old one as an orphan on re-load — on a fresh build only the
new Name is created, but re-loading an existing org needs the old records deleted (done on
ent-r1: the 2 orphans removed by Id; final state = the 2 new names only).

**262 product rebrand (DONE).** Selective "Revenue Cloud" → "Agentforce Revenue Management"
(`_ARM_RE` guarded regex in `scrub_text`, **in-app data only** — base rlm-base-dev refs untouched):
**15 changed** (standalone product-name body prose + the "& Key Modules" nav header). **Kept:**
record Names / composite keys (scrub_text never touches Name fields — e.g. "Revenue Cloud
Fundamentals/Certification"), hyperlink labels ending `Revenue Cloud</strong>` / `:</strong>`
(Trailhead module/trail/cert titles + Help-article headings), editions (" Billing"/" Advanced"),
the app/journey name (" Learning"), the release header (" Summer"), and the "Data Sheet" title.
Also: the Home green banner's old Salesforce Go setup CTA → "What's New in Summer '26"
(`rewrite_home_relnotes` — the org is already configured, so the setup/Go framing was dropped).

**Deferred (editorial — not blocking the load):**
- **Wrong-vertical WebPages** `DynamicLink` "Release Notes" → Comms Summer '24 / Energy
  Winter '25; should point at Revenue Cloud release notes.
- **1× `drive.google.com`** href (Home "Revenue Cloud Data Sheet", `1kvGZGF…`) — personal/auth-gated
  Drive file; needs an official replacement (content decision). (The Billing "Dashboard Setup" Drive
  link was replaced with the Operations Console Help article — see above.)

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
| `RLM_Learning_Icon__c` | `Name,RLM_Learning_Size__c,RLM_Learning_Type__c` |
| `RLM_Learning_Page__c` | `RLM_Learning_Active__c,Name,RLM_Learning_Type__c` |
| `RLM_Learning_Section__c` | `RLM_Learning_Active__c,RLM_Learning_Header__c,Name,RLM_Learning_Sub_Header__c,RLM_Learning_Video_Link__c,RecordType.DeveloperName,RLM_Learning_Icon__r.Name,RLM_Learning_Page__r.Name` |
| `RLM_Learning_DynamicLink__c` | `RLM_Learning_App_API_Name__c,RLM_Learning_Filter_Name__c,RLM_Learning_Identity__c,RLM_Learning_Link__c,Name,RLM_Learning_Object__c,RLM_Learning_Page_Name__c,RLM_Learning_Relationship_API_Name__c,RLM_Learning_Relative_Url__c,RLM_Learning_Setup_Page__c,RLM_Learning_Site_Name__c,RLM_Learning_Text_Value__c,RLM_Learning_Where_Condition__c,RecordType.DeveloperName,RLM_Learning_Page__r.Name,RLM_Learning_Section__r.Name` |
| `RLM_Learning_Block__c` | `RLM_Learning_ActionText__c,RLM_Learning_Active__c,RLM_Learning_Description__c,RLM_Learning_Header__c,Name,RLM_Learning_Note__c,RLM_Learning_Sub_Header__c,RLM_Learning_Action__r.Name,RLM_Learning_Icon__r.Name` |
| `RLM_Learning_SectionBlock__c` | `$$RLM_Learning_Section__r.Name$RLM_Learning_Block__r.Name$RLM_Learning_Order_Sequence__c,RLM_Learning_Section__r.Name,RLM_Learning_Block__r.Name,RLM_Learning_Order_Sequence__c` |

## Org load — verified working + SFDMU requirements

Deployed + loaded + verified on scratch org `ent-r1` (2026-06-19). The framework's
`SectionBlockController.getSectionsWithBlocksByType` returns fully-resolved sections →
blocks → icons → dynamic links. Four non-obvious requirements were needed to make SFDMU
resolve everything (each surfaced only on a live load):

1. **Lookup fields must be in the query, not just the traversal.** Each lookup needs BOTH
   the `__c` field AND the `__r.Name` traversal in the `export.json` query (e.g.
   `…, RLM_Learning_Icon__c, RLM_Learning_Page__c, RLM_Learning_Icon__r.Name, RLM_Learning_Page__r.Name`). With only the traversal, SFDMU
   drops the lookup from the insert and the foreign key lands null.
2. **RecordType is matched on a 2-part `DeveloperName;SobjectType` externalId.** A
   `RecordType` object (operation `Readonly`) is declared first in `export.json`, with a
   source `RecordType.csv` (the 19 record types). The default 3-part composite
   (`…;NamespacePrefix;…`) fails because NamespacePrefix is null on unmanaged record types
   (SFDMU's null ≠ the CSV's empty string).
3. **The running user needs record-type visibility.** `RLM_Learning` includes
   `recordTypeVisibilities` for all 19 record types — without them the insert fails with
   "Record Type ID isn't valid for the user."
4. **Permission-set hygiene:** required fields (`RLM_Learning_Icon__c.RLM_Learning_Size__c`, `RLM_Learning_Page__c.RLM_Learning_Type__c`) are
   excluded from FLS; the Section layouts' `<platformActionList>` (Chatter `RypplePost`)
   was stripped from `post_inapp` (invalid on scratch orgs).

### Junction idempotency — fixed ✅

The composite-traversal externalId on `RLM_Learning_SectionBlock__c` does **not** match on re-Upsert
(CLAUDE.md SFDMU Bug 3/5) — a live load proved a re-run doubled the 120 junction rows to 240.
**Fix applied:** `RLM_Learning_SectionBlock__c` uses **`operation: Insert` + `deleteOldData: true`**, which
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
