# Usage-metered products for customer demonstrations (durable guide)

This document captures **lessons that apply whenever you add usage-based (metered) sellable products** to a **customer demo catalog** in Revenue Cloud—regardless of industry, customer name, or SKU prefix.

**What is ephemeral:** Any one demo’s concrete data (product names, SKU prefixes like `SF-*`, rate card names, static resources, logos) can be **removed or replaced** when you onboard the next customer. **What stays in the repo** is this pattern, the **QuantumBit `qb-rating` / `qb-rates` reference shape**, and the **SFDMU plans under `datasets/sfdmu/customer-template/`** as a **worked example**—not a requirement to keep Snowflake as the brand.

**Who this is for:** Agents and humans building **PCM + rating + (optional) rates** so quotes can carry **metered lines**, **PUR / PURP / PUG** load correctly, and **delete/reload** stays safe.

**Related docs:**

| Doc | Role |
|-----|------|
| [`customer-template-usage-resource.md`](../references/customer-template-usage-resource.md) | Field-level model: **UsageResource**, **PUR**, **PURP**, **PUG**, billing policies |
| [`customer-demo-onboarding.md`](customer-demo-onboarding.md) | End-to-end **`prepare_customer_demo_catalog`** flow, Product2 CSV shape, troubleshooting |
| [`customer-template-rate-card-entry.md`](../references/customer-template-rate-card-entry.md) | **RateCardEntry** stitching for demo rate cards (**Base** vs **Tier**) |
| [`customer-template-tier-rate-card-lessons-learned.md`](../references/customer-template-tier-rate-card-lessons-learned.md) | **`RateAdjustmentByTier`**, SFDMU order, delete cascade, vs **`PriceAdjustmentTier`** |
| [`.cursor/skills/rlm-customer-demo-usage-rates/`](../../.cursor/skills/rlm-customer-demo-usage-rates/) | Triage table + file map (**SKILL.md** + **reference.md**) |

---

## 1. Reference shape: mirror QuantumBit before inventing

For **usage-metered sellable products** with **policies and grants** on **Product Usage Resource**, the stable reference in this repo is **`datasets/sfdmu/qb/en-US/qb-rating/`** (and **`qb-rates`**)—especially **`QB-DB`**:

- **Sellable usage product** with **`UsageModelType = Anchor`**
- **Usage-definition** products for **UsageResource.UsageDefinitionProduct**
- **UsageResource** rows (**Category = Usage**, UOM class + default UOM, **UsageResourceBillingPolicy**)
- **ProductUsageResource** (junction), **ProductUsageResourcePolicy**, **ProductUsageGrant**, renewal/rollover/overage helpers, **UsagePrdGrantBindingPolicy**, **RatingFrequencyPolicy**

When you design a **new** customer demo, **copy relationships and picklist values from QB first**, then rename SKUs/codes/policies. That reduces platform surprises.

---

## 2. `UsageModelType` on sellable usage SKUs (critical)

| Do | Don’t |
|----|--------|
| Use **`Anchor`** on **sellable usage** products that carry **Product Usage Resource policies** (**PURP**) in the same pattern as **`QB-DB`**. Set it in the **rating** (and **rates**, if that plan updates **Product2**) SFDMU passes. | Use **`Pack`** for that pattern on those SKUs. |

**Why:** **`Pack`** causes the platform to **reject `ProductUsageResourcePolicy`** (*“pack usage model type”* / can’t save policy). **PURP** never persists. Quote persistence may then fail (**`PlaceSalesTransactionPersistException`**, generic index errors) because the usage graph is incomplete.

**Merchandising vs data:** The line item on a quote can still *present* like a bundled/packaged offer; the **`Product2.UsageModelType`** value for **this rating model** must be **`Anchor`**, not **`Pack`**.

---

## 3. SFDMU v5: parent resolution for meters and grants

| Area | Rule |
|------|------|
| **UsageResource** | Include **`.Name`** on **unit of measure class** and **default unit of measure** columns in CSV (not only **Code** / **UnitCode**). |
| **ProductUsageGrant** | Include **`UnitOfMeasure.Name`** and **`UnitOfMeasureClass.Name`** in CSV **and** in **`export.json`** SOQL for **ProductUsageGrant**. |

**Why:** v5 often resolves lookups using parent **`Name`**. Missing names produce **`MissingParentRecordsReport.csv`** entries and **silent missing rows** in the org.

Always open **`reports/MissingParentRecordsReport.csv`** under the rating plan after a load when behavior looks wrong.

---

## 4. Product Usage Resource Policy (PURP)

- **Depends on** §2: sellable product must allow policies (**`Anchor`** for the QB-style pattern).
- **`UsageAggregationPolicy.Code`** in CSV must match an existing **`UsageResourceBillingPolicy.Code`** (shared codes like **`monthlypeak`** / **`monthlytotal`** are reusable across demos).
- **`UsageAggregationPolicyId`** on **ProductUsageResourcePolicy** references **`UsageResourceBillingPolicy`** (relationship name **`UsageAggregationPolicy`**).

---

## 5. Delete / reload order and transaction blockers

1. **Quote and order grants on meters** — Before deleting **UsageResource** rows, remove references:
   - Run **`customer_demo_purge_records`** (or equivalent) for **your** demo meter codes: today’s script targets the **example** template’s **`SF-UR-*`** codes and deletes **`QuotLineItmUseRsrcGrant`** / **`OrderItemUsageRsrcGrant`**. **When you introduce new meter codes, update that Apex** (and any scoped **delete*Rating*Data** scripts) so they match **your** prefixes.
2. **Rate card entries (Base, Tier, and `RateAdjustmentByTier`)** — Run **`delete_customer_demo_rates_data`** (or your plan’s equivalent) **before** rating delete when **RateCardEntry** still points at demo **UsageResource** rows. The template task removes **both** **`CD-DEMO`** cards and relies on **RCE** delete to cascade **RABT** (do not assume you can delete **RABT** manually after **RCE** is **Inactive** — follow the same **deactivate → delete RCE** pattern as **`deleteQbRatesData.apex`**).
3. **Rating** — Run **`delete_customer_demo_rating_data`** immediately before **`insert_customer_demo_rating_data`** on reloads.

**Duplicate PURs:** **Insert**-only **ProductUsageResource** without a prior scoped delete creates **multiple PURs** per product × meter. Always run the **documented delete** for your demo slice before re-inserting.

---

## 6. Activation

- After rating SFDMU: **`activate_rating_records`** (PUR / PUG activation ordering is handled in **`scripts/apex/activateRatingRecords.apex`**).
- After rates SFDMU: **`activate_rates`** (moves **all** non-**Active** **RateCardEntry** to **Active**, including **Tier** parents after **`RateAdjustmentByTier`** was inserted under **Draft** **RCE**).
- **CCI:** Some versions reject **`--org`** on **`cci task run activate_rating_records`**. Use **`prepare_customer_demo_catalog`** with **`--org`**, **`cci org default`**, or **`sf apex run --file scripts/apex/activateRatingRecords.apex --target-org …`**.

---

## 7. Quotes: what to put on the line

- **Sellable usage SKUs** (the products customers “buy” on the quote) — in the example template, that role is the **`SF-USG-*`** rows; for another customer, your **equivalent** sellable SKUs.
- **Not** the **usage-definition-only** products wired to **UsageResource.UsageDefinitionProduct** (in the example, **`SF-BLNG-*`**)—those back **meters**, not normal quote merchandising.

After a **full demo data reload**, **re-add usage lines** or use a **new quote** so **QLIURG**-style children match the current **PUR / PURP / PUG**.

**API name note:** Quote line usage grants are **`QuotLineItmUseRsrcGrant`** in SOQL/API.

---

## 8. Verification checklist (any demo)

After loading PCM + rating (+ rates):

| Check | Intent |
|-------|--------|
| **Sellable usage `Product2.UsageModelType`** | **`Anchor`** for QB-style metered + PURP pattern |
| **PURP** | At least one **ProductUsageResourcePolicy** per **PUR** you expect |
| **PUG** | **ProductUsageGrant** rows tied to **definition** products / PURs per your design |
| **Rate cards (if loaded)** | **Base** **RCE** has **`Rate`**; **Tier** **RCE** has **empty `Rate`** and child **`RateAdjustmentByTier`** bands in the consumption UOM of the line |
| **PSM on every RCE** | Matches **Standard PricebookEntry** for that sellable usage SKU (**`customer-pricebook-entries.csv`** in the template) |
| **MissingParent report** | Empty or explained |

Adjust SOQL filters from example **`SF-%`** prefixes to **your** SKU pattern. **Do not** confuse **`RateAdjustmentByTier`** (rate card) with **`PriceAdjustmentTier`** (**`PriceAdjustmentSchedule`**).

---

## 9. Replacing the example customer (Snowflake or any other)

When the **next** practice or customer replaces the current demo:

1. **Keep** this guide, **`customer-template-usage-resource.md`**, **`qb-rating`**, and the **flow/tasks** pattern.
2. **Replace or fork** dataset CSVs, static resources, pricebook CSV, and **Apex delete/purge lists** so SKU/code sets match the new demo.
3. **Re-validate** §2–§4 and **`MissingParentRecordsReport.csv`** on first load.
4. **Do not** revert **`UsageModelType`** to **`Pack`** for sellable usage rows that need **PURP** unless Salesforce documents a different supported combination for your scenario.

---

## 10. Out of scope

- **Wiping every PCM row** with one command (no universal “delete all demo products” task; use targeted deletes or org refresh).
- **Root-cause fixes** inside managed **Place** / transaction code—escalate to **Salesforce Support** with logs if data shape matches this guide and errors persist.

---

## See also

- **`AGENTS.md`** → Customer Demo Product Onboarding UX  
- **`datasets/sfdmu/customer-template/en-US/customer-template-rating/README.md`** (example plan)  
- **`datasets/sfdmu/qb/en-US/qb-rating/`** (canonical reference load)
