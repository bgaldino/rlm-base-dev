# Headless Configurator Context Mapping — Setup Plan

> **Status:** Path 1 implemented — pending scratch org validation of Path 2
> **Relates to:** `feat/rlm-portal` branch, `rlm-webapp/` configurator modal
> **Last updated:** 2026-03-21

---

## Background

The `ProductConfiguratorModal` calls `headlessConfigLoad(quoteId)` → `POST /connect/cpq/configurator/load` to initialise an interactive configuration session after a Quote is created via `placeSalesTransaction`. On the current development org this returns:

```
404 The requested resource does not exist
```

The root cause is that `headlessConfigLoad` performs an **automatic context mapping lookup** — it queries the product on the QuoteLineItem to find its associated Configurator Context Mapping. If no such association exists for the product, the endpoint has nothing to load and returns 404.

This document describes:
1. What a Configurator Context Mapping is and how it works
2. Two resolution paths (explicit init vs. product-level setup)
3. The CCI task approach for automating the setup in scratch orgs and sandboxes

---

## Architecture: Two Ways to Init the Headless Configurator

The headless configurator has two initialisation endpoints:

| Endpoint | How it finds the context | When it works |
|---|---|---|
| `POST /connect/cpq/configurator/load` | Auto-discovers from the product on the QuoteLineItem → looks up that product's linked ContextMapping record | Only works if the product has a ContextMapping association set up in the org |
| `POST /connect/cpq/configurator/set` | Caller provides `contextMappingId` + a `transaction` JSON seed | Works whenever a ContextMapping ID is known, regardless of product setup |

Both return `{ success: bool, contextId: string }` and the rest of the session lifecycle (Get, AddNodes, UpdateNodes, Save) is identical.

The **existing repo infrastructure** already creates `QuoteEntitiesMapping` inside `RLM_SalesTransactionContext` via the `ConstraintEngineNodeStatus` context plan. That mapping ID is what both paths ultimately need.

---

## Path 1 — Short-Term: Use `headlessConfigSet` in the Portal

Instead of `headlessConfigLoad(quoteId)`, query the `QuoteEntitiesMapping` context mapping ID dynamically at runtime and call `headlessConfigSet(contextMappingId, transaction)`.

### How `headlessConfigSet` works

```
POST /services/data/v66.0/connect/cpq/configurator/set
{
  "contextMappingId": "<QuoteEntitiesMapping ID>",
  "transaction": "{\"Quote\":[{\"businessObjectType\":\"Quote\",\"id\":\"<quoteId>\"}]}"
}
→ { "success": true, "contextId": "..." }
```

The `transaction` parameter is a JSON-serialised seed that tells the configurator which Quote to hydrate from. The `businessObjectType` must be `"Quote"` for the quote-based flow.

### Changes needed in `rlmApi.js`

Add a helper to fetch the `QuoteEntitiesMapping` context mapping ID:

```javascript
// Cache the mapping ID after the first lookup to avoid repeated SOQL
let _quoteEntitiesMappingId = null;

export async function fetchQuoteEntitiesMappingId(auth) {
  if (_quoteEntitiesMappingId) return _quoteEntitiesMappingId;
  const soql = `SELECT Id FROM ContextMapping
                WHERE DeveloperName = 'QuoteEntitiesMapping' LIMIT 1`;
  const rows = await query(auth, soql);
  _quoteEntitiesMappingId = rows?.[0]?.Id ?? null;
  return _quoteEntitiesMappingId;
}
```

### Changes needed in `ProductConfiguratorModal.jsx`

In `loadHeadless`, replace the single `headlessConfigLoad` call with a two-path attempt:

```javascript
const loadHeadless = useCallback(async (txId) => {
  setLoadingMsg('Loading configurator…');

  // Attempt 1: auto-discover via headlessConfigLoad (works when product has a ContextMapping)
  let loadResult = await headlessConfigLoad(auth, { transactionId: txId })
    .catch(() => null);

  // Attempt 2: explicit seed via headlessConfigSet (works when QuoteEntitiesMapping exists)
  if (!loadResult?.success) {
    const mappingId = await fetchQuoteEntitiesMappingId(auth);
    if (mappingId) {
      const transaction = JSON.stringify({
        Quote: [{ businessObjectType: 'Quote', id: txId }],
      });
      loadResult = await headlessConfigSet(auth, {
        contextMappingId: mappingId,
        transaction,
      }).catch(() => null);
    }
  }

  if (!loadResult?.success) {
    throw new Error(loadResult?.errors?.[0]?.message ?? 'Configurator load failed');
  }
  // ... rest of loadHeadless unchanged
}, [auth?.accessToken]);
```

This is non-destructive — if `headlessConfigLoad` starts working (because the product-level association is added later), the fallback is never reached.

---

## Path 2 — Long-Term: Product-Level Configurator Context Association

For `headlessConfigLoad` to auto-discover the context, each Bundle product needs a **ContextMapping record** linked to it. In Spring '26, this is done via:

1. **Setup UI:** Revenue Cloud > Product Configurator > Context Mappings — set the default mapping per product
2. **Metadata/API:** The `ProductRelatedComponent` or a dedicated `ProductConfiguratorContextMapping` SObject (exact SObject name is version-dependent; verify in the target org with `sf sobject list`)
3. **CCI task:** A new task that queries the target products and creates the association via the REST API

The correct metadata/SObject approach needs to be confirmed against the actual org schema in the scratch org, since this area changed between Release 258 and 260.

### Proposed CCI task: `setup_configurator_context`

```yaml
# cumulusci.yml — under tasks:
setup_configurator_context:
  group: Portal — rlm-webapp
  description: >
    Associates Bundle products with the QuoteEntitiesMapping configurator context
    so that the headless configurator (headlessConfigLoad) can auto-discover the
    context when a quote is placed. Runs an Apex script to create the association
    records; idempotent (skips products already associated).
  class_path: cumulusci.tasks.salesforce.RunApex
  options:
    apex: scripts/apex/setupConfiguratorContext.apex
```

### Proposed Apex script: `scripts/apex/setupConfiguratorContext.apex`

```apex
// setupConfiguratorContext.apex
// Creates ProductConfiguratorContextMapping records (or equivalent) for all
// Bundle products that don't already have one.  Idempotent.
//
// NOTE: The exact SObject name must be confirmed against the target org schema.
// Run `sf sobject list --target-org <alias>` and look for *Configurator* or
// *ContextMapping* SObjects introduced in Release 260.

// Step 1 — Find the QuoteEntitiesMapping context mapping record
ContextMapping mapping = [
  SELECT Id FROM ContextMapping
  WHERE DeveloperName = 'QuoteEntitiesMapping'
  LIMIT 1
];

// Step 2 — Find Bundle products that need the association
// (Replace 'Bundle' with the ProductType value used in this org)
List<Product2> bundles = [
  SELECT Id, Name, ProductCode
  FROM Product2
  WHERE Type = 'Bundle' AND IsActive = true
];

// Step 3 — Create associations (SObject name TBD — verify against org schema)
// Example shape; adjust SObject + fields to match what the org exposes:
//
// List<ProductConfiguratorContextMapping__c> records = new List<ProductConfiguratorContextMapping__c>();
// for (Product2 p : bundles) {
//   records.add(new ProductConfiguratorContextMapping__c(
//     Product__c          = p.Id,
//     ContextMappingId__c = mapping.Id
//   ));
// }
// insert records;

System.debug('Found ' + bundles.size() + ' bundle products and mapping ' + mapping.Id);
System.debug('TODO: confirm SObject name and insert associations');
```

The script is intentionally left as a stub with the `System.debug` output until the scratch org is spun up and the SObject schema can be verified.

---

## Build Flow Integration

Once the SObject name is confirmed and the Apex script is complete, the task fits into the build flow as follows:

```
prepare_rlm_org flow
  └── deploy (existing metadata, includes ProductConfigurator.settings)
  └── insert_qb_pcm_data  (QB products including QB-COMPLETE)
  └── insert_qb_pricing_data
  └── activate_rating_records
  └── setup_configurator_context   ← NEW: run after products are loaded + activated
```

The `setup_configurator_context` task should run **after** product data is loaded (so the Bundle products exist) and **before** portal testing begins.

For the TSO flow:

```
prepare_tso flow
  └── ... existing steps ...
  └── setup_configurator_context   ← same task, same position
```

---

## Verification

After `setup_configurator_context` runs, verify by opening the portal, clicking Configure on QuantumBit Complete Solution, and observing that the left panel shows the bundle component tree (headless context loaded) rather than "This product is ready to add to your quote."

Alternatively, verify via SOQL in the org:

```sql
SELECT Id, DeveloperName FROM ContextMapping WHERE DeveloperName = 'QuoteEntitiesMapping'
```

And check that the product has a mapping association (SObject name TBD).

---

## Open Items

| # | Question | Where to verify |
|---|---|---|
| 1 | Exact SObject name for product-to-context-mapping association | `sf sobject list --target-org scratch` — look for *Configurator* or *ContextMapping* SObjects |
| 2 | Whether `headlessConfigSet` with `QuoteEntitiesMapping` is sufficient for QB-COMPLETE, or whether a product-type-specific mapping is required | Test Path 1 in scratch org |
| 3 | Whether QB-COMPLETE has `ProductRelatedComponent` records (bundle children) defined in the qb-pcm data plan | Review `datasets/sfdmu/qb/en-US/qb-pcm/` export.json and CSVs |
| 4 | Whether bundle children appear in the configurator's component tree once a valid context is loaded | End-to-end test in scratch org |
| 5 | `IndustriesConfiguratorPlatformApi` permission set — is it assigned to the running user in the portal? | Check `unpackaged/post_tso_*/` permission set assignments |
