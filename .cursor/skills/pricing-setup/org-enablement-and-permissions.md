# Org Enablement and Permissions

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264 / API v68.0. Sources:
> `ind.pricing_turn_on_salesforce_pricing.htm`, `ind.pricing_set_up_salesforce_pricing.htm`,
> `ind.pricing_salesforce_pricing.htm`, `ind.pricing_essentials.htm`,
> `ind.pricing_understand_advanced_pricing_setup.htm`, `ind.pricing_configure_salesforce_pricing_objects.htm`,
> `ind.pricing_permissions_salesforce_pricing.htm`, `ind.pricing_record_sharing_pricing.htm`,
> `ind.pricing_access_your_pricing_information.htm`, `ind.pricing_einstein_generative_ai_for_salesforce_pricing.htm`,
> `ind.pricing_set_up_einstein_generative_ai_for_salesforce_pricing.htm`,
> `ind.pricing_get_ready_to_build_pricing_procedures.htm`, `ind.pricing_set_up_price_waterfall_salesforce_pricing.htm`;
> repo: `unpackaged/pre/2_settings/IndustriesPricing.settings-meta.xml`,
> `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`, `cumulusci.yml`,
> `docs/references/revenue-cloud-permissions.md`. Not live-verified.

What has to be on, licensed, assigned and shared before a pricing procedure can be built or
run. Everything downstream (decision tables, recipes, procedures, runtime APIs) assumes this.

## When you need it

- A new org where pricing objects or the Salesforce Pricing Setup page are missing.
- A user cannot see the Price Management app, edit procedures, or call pricing APIs.
- A runtime user prices nothing or sees no price book rows (sharing).
- Before building any procedure: run the prerequisites checklist below.

## Set it up

Edition gate: Enterprise, Unlimited, Developer editions of Revenue Management with the Revenue
Cloud Growth or Advanced license. Supported products also include Health, Communications,
Energy & Utilities, Insurance, Financial Services, Media Cloud and Asset Service Lifecycle
Management (Enterprise, Performance, Unlimited). Lightning Experience only. [Help]
`ind.pricing_permissions_salesforce_pricing.htm`

1. **Turn on Salesforce Pricing** (System Admin): Setup > Quick Find "Salesforce Pricing" >
   Salesforce Pricing Settings > turn on Salesforce Pricing. [Help] `ind.pricing_turn_on_salesforce_pricing.htm`
2. **Licenses and users**: assign permission set licenses and permission sets (table below). A
   user has one profile and many permission sets. [Help]
3. **Basic setup** (Help's recommended base, required before any custom solution): [Help]
   `ind.pricing_set_up_salesforce_pricing.htm`

| # | Basic setup step | Detail lives in |
|---|---|---|
| 1 | Configure decision tables | [decision-tables](../decision-tables/SKILL.md) |
| 2 | Pricing recipes setup (decision tables associated to objects, used by procedures) | [pricing-recipes](pricing-recipes.md); repo build: [pricing-wiring](../pricing-wiring/SKILL.md) |
| 3 | Select a pricing procedure (clone a template; a template is not executable) | [operations-and-troubleshooting section 1](../pricing-procedures/operations-and-troubleshooting.md#1-which-procedure-does-the-org-run) |
| 4 | Sync pricing data (active decision tables mapped to a recipe; Help adds usage type Pricing, core does not filter on it) | [import-export-and-bulk-data](./import-export-and-bulk-data.md#sync-pricing-data) |
| 5 | Set up Price Waterfall (configure + persistence; needs Design Time) | [runtime-and-observability](../pricing-procedures/runtime-and-observability.md) |
| 6 | Set up Price Logs Capture | [runtime-and-observability](../pricing-procedures/runtime-and-observability.md) |
| 7 | Configure Salesforce Pricing objects (page layouts) | below |
| 8 | Configure record sharing | below |

Procedure selection has three separate settings (Revenue Settings, Salesforce Pricing Setup,
Product Discovery Settings); see [operations-and-troubleshooting section 1](../pricing-procedures/operations-and-troubleshooting.md#1-which-procedure-does-the-org-run). Not repeated here.

### Essentials vs advanced setup

"Essentials" in Help (`ind.pricing_essentials.htm`) is a **glossary** (terms, key objects), not
a setup tier; setup tiers are basic (above) and advanced. [Help]
Advanced setup (`ind.pricing_understand_advanced_pricing_setup.htm`) is optional, per feature:

| Advanced item | Owner |
|---|---|
| Price Tracking history settings | [price-tracking](../pricing-procedures/elements/price-tracking.md) |
| Proration settings | [proration-and-subscription](../pricing-procedures/elements/proration-and-subscription.md) |
| Parallel pricing element execution | [runtime-and-observability](../pricing-procedures/runtime-and-observability.md) |
| Advanced price log settings | [runtime-and-observability](../pricing-procedures/runtime-and-observability.md) |
| Einstein generative AI for pricing | below |
| Pricing action parameters for standard objects | Help `ind.pricing_configure_pricing_action_parameters_for_standards_objects.htm` (not summarized here) |

Also in the Help hub: import/export of pricing metadata (recipes, decision tables, context
definitions, procedures) as a packaged file, price books and cost books, Price Adjustment
Schedules, and limits (`ind.pricing_limits.htm`). [Help] `ind.pricing_salesforce_pricing.htm`

### Salesforce Pricing settings, one row each

| Setting (Setup) | Effect | Details |
|---|---|---|
| Salesforce Pricing (on/off) | Enables the pricing objects and features | this file |
| Price Waterfall | Step-by-step breakdown of a priced transaction | [runtime-and-observability](../pricing-procedures/runtime-and-observability.md) |
| Price Waterfall Persistence | Stores waterfall detail for later audit | [runtime-and-observability](../pricing-procedures/runtime-and-observability.md) |
| Price Logs Capture | Captures pricing API logs for the Pricing Operations Console | [runtime-and-observability](../pricing-procedures/runtime-and-observability.md) |
| Advanced price log settings | Finer-grained log categories | [runtime-and-observability](../pricing-procedures/runtime-and-observability.md) |
| Parallel element execution | Runs elements concurrently | [runtime-and-observability](../pricing-procedures/runtime-and-observability.md) |
| Price Tracking history | Retention of tracked price history | [price-tracking](../pricing-procedures/elements/price-tracking.md) |

### Configure Salesforce Pricing objects (page layouts)

Requires Salesforce Pricing Design Time. [Help] `ind.pricing_configure_salesforce_pricing_objects.htm`

1. Setup > Object Manager > **Product** > Page Layouts > Product Layout > Related Lists: add
   Price Adjustment Tier, Attribute Based Adjustment, Bundle Based Adjustment, Parent Products,
   Derived Products, Source Products.
2. **Price Book Entry** > Page Layouts: add the Product Selling Model field. It cannot be
   changed after creation; for a different model, deactivate the entry and create a new one.
3. **Price Adjustment Schedule** > Page Layouts: add the Attribute Based Adjustment related list.

If you customize standard layouts (Opportunity, Work Order), include the parent record as a
field and use custom actions, not URL buttons; otherwise the product lookup cannot find price
book entries. [Help]

## Fields and rules

### Permission sets and licenses

Help names three personas plus one analyst role. The Help table lists license/permission set
names as UI labels; API names below are from this repo's shipped metadata. [Help] [Repo]

| Persona (Help) | UI permission set / license | Grants (Help) | API name [Repo] |
|---|---|---|---|
| Pricing Admin | Salesforce Pricing Admin + Design Time User | Turn on Salesforce Pricing; create/manage all pricing objects and features; manage recipes, decision tables and recipe mappings; turn on Price Waterfall and Persistence | `CorePricingAdmin`, `CorePricingDesignTimeUser` |
| Pricing Design Time User (designer) | Salesforce Pricing Design Time User (inferred; Help leaves this cell blank) | All pricing elements and the pricing procedure feature; also decision tables and procedures [Help: `ind.pricing_get_ready_to_build_pricing_procedures.htm`] and waterfall settings (waterfall setup articles) | `CorePricingDesignTimeUser` (license `CorePricingDesignTime`) |
| Runtime user | Salesforce Pricing Run Time User | Read-only pricing data; can call Salesforce Pricing APIs; Run Decision Matrices and Run Expression Sets by default | `CorePricingRunTimeUser` |
| Pricing Analyst | (Price Management app access) | Price Management app plus create/read/update/delete on pricing records | `CorePricingManager` (inferred mapping; Help gives no permission set name) |

Full per-set and per-group lists: [revenue-cloud-permissions](../../../docs/references/revenue-cloud-permissions.md).

### Record sharing

Setup > Security > Sharing Settings > Edit. [Help] `ind.pricing_record_sharing_pricing.htm`

| Object | Runtime-user access |
|---|---|
| All pricing objects | Organization-wide default Public Read Only, per your security needs |
| Price Book | View only |
| Expression Set (pricing procedures) | Public Read Only |
| Price Adjustment Schedule | Public Read Only |

Pricing API calls rely on permission sets (read on entities, execute logic), so sharing rules
are optional for API calls but still needed for UI access. [Help] Requires Manage Sharing.

### Access pricing information (UI)

[Help] `ind.pricing_access_your_pricing_information.htm`: pricing data shows in dedicated
Lightning components, switchable between a grid and a list view. The **Pricing Discount
Calendar** shows all price adjustment schedule types (Volume, Attribute, Bundle) for a product
across dates, groupable by type and filterable; discounts are editable from it. Aimed at the
analyst persona.

## How pricing uses it

- The runtime user permission set is what lets Place Sales Transaction, Calculate Prices and
  Simulate execute procedures and read decision tables; see
  [operations-and-troubleshooting](../pricing-procedures/operations-and-troubleshooting.md).
- Design Time gates creating context definitions, decision tables and procedures. [Help] Core gates
  saving a procedure (Expression Set create/edit/delete) on Expression Set admin access instead:
  `InteractionCalcAdminPerm`, or Customize Application / Modify All Data; Design Time gates the
  pricing setup records and actions. Whether the Design Time permission set carries
  `InteractionCalcAdminPerm` is not verified. [Core]
- Product Selling Model on the price book entry is what list-price decision tables key on; see
  [list-price](../pricing-procedures/elements/list-price.md).

### Einstein generative AI for pricing

[Help] `ind.pricing_einstein_generative_ai_for_salesforce_pricing.htm` (permission),
`ind.pricing_set_up_einstein_generative_ai_for_salesforce_pricing.htm` (steps)

- What it does: on a pricing element, suggests variable-to-context-tag mappings with confidence
  scores; you review and approve before they are deployed into the context definition.
  Wrong tags corrupt downstream elements that read earlier outputs, which is the motivation.
- Set up: needs Customize Application. Setup > Einstein Setup > turn on Einstein. Help says
  users also need "required permissions" but names none (see Open questions).
- Tag mapping itself: [operations-and-troubleshooting section 7](../pricing-procedures/operations-and-troubleshooting.md#7-context-tag-mapping).

### Prerequisites checklist (before building procedures)

[Help] `ind.pricing_get_ready_to_build_pricing_procedures.htm`. Design Time is required to
create context definitions, create/edit/activate decision tables, and create/update/delete procedures.

- [ ] Decision tables exist and are active ([decision-tables](../decision-tables/SKILL.md)).
- [ ] Context definition with nodes, attributes, context tags and mappings
      ([context-service](../context-service/SKILL.md)). A context tag cannot share a name with
      a decision table's label or API name.
- [ ] Every sellable product has a price book entry in a price book.
- [ ] Product selling models configured (one-time, term-defined, evergreen) and used on entries.
- [ ] Constant resources created for any variable that has no context tag.
- [ ] Basic setup steps 1-8 above done; users hold the right permission sets; sharing set.

## Data and automation

- Settings metadata: `IndustriesPricingSettings` carries the toggle `enableSalesforcePricing`
  plus waterfall, persistence, debug-log and parallelization flags. [Repo]
  `unpackaged/pre/2_settings/IndustriesPricing.settings-meta.xml` ships the toggle, waterfall,
  persistence, debug price logs and parallelization on, large-transaction pricing off.
- `RevenueManagementSettings` (`unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`)
  carries pricing-adjacent switches, e.g. `enableDeltaPricing`, `enableAdvancedDetailLinePricing`,
  `enableRevInstPricingDefaultPref`. [Repo] The comments in that file are the rationale.
- Licenses: `cumulusci.yml` `rlm_psl_api_names` assigns PSL `CorePricingDesignTime`. Persona
  groups: `RLM_Product_and_Pricing_Admin` bundles `CorePricingAdmin`, `CorePricingDesignTimeUser`,
  `CorePricingManager`, `CorePricingRunTimeUser`; `RLM_Sales_Representative` and
  `RLM_Sales_Operations` carry only `CorePricingRunTimeUser`. [Repo]
- The default procedure is set by the Robot-driven tasks `configure_core_pricing_setup` (Salesforce
  Pricing Setup page) and the revenue settings task; see [pricing-wiring](../pricing-wiring/SKILL.md). [Repo]

## Verify

```bash
sf data query --target-org <sf_alias> -q "SELECT PermissionSet.Name, Assignee.Username FROM PermissionSetAssignment WHERE PermissionSet.Name LIKE 'CorePricing%'"
sf data query --target-org <sf_alias> -q "SELECT PermissionSetLicense.DeveloperName, Assignee.Username FROM PermissionSetLicenseAssign WHERE PermissionSetLicense.DeveloperName LIKE 'CorePricing%'"
sf project retrieve start --target-org <sf_alias> -m Settings:IndustriesPricing   # enableSalesforcePricing
```

UI: Setup > Salesforce Pricing Settings shows the toggle on; sign in as a runtime user and run
Simulate or a quote reprice (see [operations-and-troubleshooting](../pricing-procedures/operations-and-troubleshooting.md)).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Salesforce Pricing Settings page missing | Edition/license lacks Revenue Cloud Growth or Advanced; not System Admin | Check license; use a System Admin |
| Cannot edit procedures or decision tables | No Design Time permission set; for procedures, no Expression Set admin access [Core] | Assign Design Time User; for procedure saves also check `InteractionCalcAdminPerm`, Customize Application or Modify All Data |
| Runtime user: no price book rows in UI | Org-wide default private for Price Book / Expression Set / Price Adjustment Schedule | Set sharing as above |
| API prices but UI shows nothing | Sharing is optional for API, required for UI | Add sharing |
| Product lookup fails on Opportunity/Work Order | Customized layout or URL button lost context | Add parent field, use custom action |
| Cannot change selling model on an entry | Field is immutable after create | Deactivate entry, create new |

## Open questions

- Help does not name the permission sets or licenses needed for the Einstein generative AI
  feature (this repo's TSO list carries `EinsteinGPTGetProductPricingPsl`, which is a different
  Sales Cloud feature as far as the docs show; no link established).
- The Help persona table lists labels only; the analyst-to-`CorePricingManager` mapping above is
  inferred from the repo's group composition. The designer row's permission-set cell is blank in
  Help; the label above is inferred from the persona name and from the admin row, which lists
  Salesforce Pricing Design Time User.
- Help's note that Run Time users have Run Decision Matrices / Run Expression Sets "by default"
  was not checked against the shipped permission set contents.
