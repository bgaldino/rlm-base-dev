# Dependency Ordering Rules

## Metadata Deploy Ordering

### Pre-deploy numbered directories

`unpackaged/pre/` subdirectories deploy alphabetically (numbered prefixes
control order):

| Dir | Deploys | Why First |
|-----|---------|-----------|
| `1_objects/` | Custom fields | Fields must exist before PSGs/DTs that reference them |
| `2_settings/` | Org settings | Features must be enabled before metadata that uses them |
| `3_permissionsetgroups/` | PSGs | PSG metadata deploys here; references PSLs from `force-app/` |
| `5_decisiontables/` | Decision table definitions | Must exist before expression sets or flows reference them |

### Profile strip-and-build

The `force-app/` Admin profile is **classAccesses only**:
- Step 5 (`deploy_full`): profile with no layout assignments
- Step 29 (`prepare_ux`): full profile from `templates/profiles/base/` + patches

### Object metadata strip-and-build

These standard objects have `actionOverrides` and `compactLayoutAssignment`
in `templates/objects/base/` (NOT `force-app/`):
- Asset, Quote, Order, OrderItem, QuoteLineItem, FulfillmentOrderLineItem

They deploy at step 29 after referenced flexipages exist. The `force-app/`
paths are forceignored.

### Metadata dependencies

| Depends On | Must Deploy First | Reason |
|-----------|-------------------|--------|
| Custom fields | `unpackaged/pre/` or `force-app` | Referenced by flows, LWC, Apex |
| Expression sets | `force-app/expressionSetDefinition/` | Referenced by pricing/rating procedures |
| Decision tables | `unpackaged/pre/5_decisiontables/` | Referenced by pricing/rating flows |
| Permission sets | `force-app/permissionsets/` | Must exist before assignment |
| Context definitions | Extended at runtime | Created by `extend_context_*` tasks |
| Flexipages/compact layouts | `templates/` → `unpackaged/post_ux/` | Referenced by actionOverrides |

---

## Data Dependencies

| Load Order | Plan | Depends On |
|-----------|------|------------|
| 1 | qb-pcm (products) | None |
| 2 | qb-pricing | qb-pcm |
| 3 | qb-billing | qb-pcm |
| 4 | qb-tax | qb-pcm |
| 5 | qb-dro | qb-pcm |
| 6 | qb-rating | qb-pcm |
| 7 | qb-rates | qb-pcm + qb-rating (PURs must exist) |
| 8 | qb-clm | qb-pcm |
| 9 | qb-approvals | post_approvals metadata + email templates |

## Deletion Order

Reverse dependency order (children before parents):
1. Delete rates data (FK to PURs)
2. Delete rating data (PUG → PURP → PUR)
3. Delete billing data
4. Delete pricing data
5. Delete PCM data (products last)

---

## Data vs Metadata — Choosing the Right Mechanism

| What You're Creating | Mechanism | Why |
|---------------------|-----------|-----|
| Object/field definitions, LWC, Apex, flows | Metadata API deploy | Declarative metadata |
| Bulk records (products, prices, policies) | SFDMU data plan | Bulk load with externalId matching |
| Context definition attributes | Connect API (Python task) | No Metadata API support |
| Lightning Email Templates (approval) | REST API sidecar task | EmailTemplatePage can't deploy |
| Procedure Plan definitions | Connect API (Python task) | API-only creation |
| Setup page toggles | Robot Framework | No API equivalent |
| Org settings (pricing/billing enabled) | Settings XML | Standard metadata |
| App Launcher ordering | Aura XHR (Robot task) | SortOrder is platform read-only |
| Record state changes (activate/deactivate) | Apex script or management task | Requires DML with constraints |

---

## Post-Load Activation Patterns

| What | Activation Task | Key Constraint |
|------|----------------|----------------|
| PUR/PUG (rating) | `activate_rating_records` (7-step Apex) | PURs activate in dependency order; TokenResourceId conflict |
| Decision tables | `activate_decision_tables` / `refresh_dt_*` | Deactivate before deploy; refresh after all data loaded |
| Expression set versions | `activate_and_deploy_expression_sets` | Must set Rank before activation |
| Billing treatments | No explicit activation | Active records can never be deleted |
| Flows | `manage_flows` (activate) | Version management |
| DocGen templates | `activate_docgen_templates` | Binary content fix runs after |

---

## `prepare_rlm_org` Step Ordering

| Step | Sub-flow | What happens |
|------|---------|--------------|
| 1 | prepare_core | PSLs, PSGs, context defs, deploy_pre |
| 2 | prepare_decision_tables | DT lifecycle |
| 3 | prepare_expression_sets | ES lifecycle |
| 5 | deploy_full | `force-app/` bundle |
| 9 | prepare_quantumbit | QB metadata |
| 10 | prepare_product_data | PCM, Q3, product images |
| 11 | prepare_pricing_data | Pricing |
| 12 | prepare_docgen | DocGen |
| 13 | prepare_dro | DRO |
| 14 | prepare_tax | Tax |
| 15 | prepare_billing | Billing |
| 18 | prepare_rating | Rating + rates + activation |
| 22 | prepare_prm | PRM community + data |
| 24 | prepare_constraints | Constraints + CML |
| 26 | prepare_revenue_settings | Revenue Settings (Robot) |
| 29 | prepare_ux | UX assembly + deploy |
| 31 | stamp_git_commit | Always last |
