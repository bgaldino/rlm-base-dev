# Partner Relationship Management (PRM) Metadata

This directory contains the baseline Partner Relationship Management metadata for Revenue Cloud Base Foundations: Channel Program custom fields, permission sets, and Experience Cloud site configuration.

## Overview

The baseline PRM feature enables partner-channel setup through:

- Partner account relationships and hierarchies
- Channel program management with discount tiers
- Partner Central community site (rlm1)

PRM pricing-specific fields, flows, decision tables, pricing procedures, and
context extensions live in `unpackaged/post_prm_pricing/` and are deployed only
through the `prm_pricing` feature path.

## Contents

### Custom Fields

**ChannelProgramLevel (3 fields):**

- `RLM_Deal_Expiration_Days__c` - Number field for deal expiration period
- `RLM_Discount_Rate__c` - Number field (0 decimal places) for discount rate
- `RLM_Minimum_Deal_Size__c` - Currency field for minimum deal size threshold

**ChannelProgramMember (3 fields):**

- `RLM_Adjustment_Type__c` - Text field (255 chars) for adjustment type
- `RLM_Adjustment_Value__c` - Number field (2 decimal places) for adjustment value
- `RLM_Discount_Rate__c` - Number field (2 decimal places) for discount rate

### PRM Pricing Extension

The optional `prm_pricing` feature contributes the pricing-specific metadata
that used to be described here:

- Account, Quote, and QuoteLineItem distributor pricing fields
- `RLM_Create_New_Quote` and `RLM_Update_Channel_Program_Member`
- `RLM_Channel_Program_Level_Partner`
- `RLM_PRM_DISTI_Pricing_Procedure`
- `RLM_PRM_Pricing`
- additive PRM pricing context mappings and Tooling API recipe table mappings

See `unpackaged/post_prm_pricing/README.md` for the deployment path and
ownership details.

### Permission Sets (2)

- `RLM_PRM.permissionset-meta.xml` - Grants access to the baseline PRM channel-program fields
- `RLM_Partner_Community_User_Perm_Set.permissionset-meta.xml` - Comprehensive permissions for partner community users (107KB)

### Profile

- `RLM Custom Partner Community User.profile-meta.xml` - Custom partner community profile with 32 user permissions and Apex access

### Experience Cloud Site

**Network:**

- `rlm.network` - Partner Central community (status: UnderConstruction, URL prefix: partners)

**Experience (rlm1):**

- 57 routes and 57 views configured
- Includes record lists, record details, dashboards, opportunities, quotes, accounts, etc.
- Theme: partnerCentralEnhanced
- Variation: quoteDetailPRMUserQuoteDetailFlexPage

**Navigation:**

- `RLM_Default_Navigation.navigationMenu` - Main navigation menu
- `Default_User_Profile_Menu.navigationMenu` - User profile menu
- `RLM_Default_User_Profile_Menu.navigationMenu` - RLM-specific user profile menu

### Other Assets

- 2 content assets (DALLE image, QuantumBit logo)
- ExperienceBundle settings

## Deployment

Deploy this metadata bundle using:

```bash
cci task run deploy_post_prm --org <org-alias>
```

This task is automatically included in the baseline `prepare_prm` flow:

```bash
cci flow run prepare_prm --org <org-alias>
```

The baseline `prepare_prm` flow (main-compatible) includes the following
numbered steps. Step 4 is intentionally unused in `cumulusci.yml`; step 11 runs
the optional PRM pricing extension when `prm_pricing=true`.

1. Create Partner Central community
1. Patch network metadata (email placeholder)
1. Deploy post_prm metadata
1. Revert network metadata
1. Publish Partner Central community
1. Deploy sharing rules
1. Assign permission sets
1. Load QuantumBit PRM data
1. Apply PartnerAccount context extension (`manage_context_definition`)

When `prm_pricing=true`, `prepare_prm` also invokes `prepare_prm_pricing`, which runs
PRM pricing tasks:

- Deploy non-site PRM pricing metadata components from `unpackaged/post_prm_pricing/`
- Ensure PRM pricing recipe table mappings; shared cost-book mapping is owned by
  the core `prepare_expression_sets` path
- Apply additive PRM pricing context extensions
- Assign `RLM_PRM_Pricing`
- Insert `qb-prm-pricing` overlay data when `qb=true`
- Activate PRM pricing expression set versions
- Deactivate, load, verify, and reactivate PRM procedure-plan overlay data when
  `procedureplans=true`

## Data Loading

Sample partner data is loaded via SFDMU:

```bash
cci task run insert_quantumbit_prm_data --org <org-alias>
```

The data plan loads:

- Pass 1: Partner Accounts, Channel Programs, Channel Program Levels
- Pass 2: Enable IsPartner on Accounts, Channel Program Members

**Note:** The baseline `qb-prm` plan does not populate PRM pricing account
self-lookups. `RLM_Primary_Reseller__c` and `RLM_Primary_Distributor__c` live in
the `prm_pricing` bundle and are populated by the `qb-prm-pricing` overlay plan.

## Feature Flags

Enable PRM in `cumulusci.yml`:

```yaml
project_config:
  project__custom__:
    prm: true                    # Core PRM feature
    prm_exp_bundle: true         # Experience Cloud site content
    prm_pricing: false           # Set true to include PRM pricing metadata/tasks
```

## Pricing Integration Status

The PRM workbook (`Change Log.xlsx`) is now mapped to repository-owned artifacts using the hybrid ownership model:

- **PRM-specific procedure:** `RLM_PRM_DISTI_Pricing_Procedure` is stored in `post_prm_pricing`.
- **Shared/default procedures:** `RLM_DefaultPricingProcedure` remains in `force-app`, and `RLM_Price_Distribution_Procedure` remains in `post_procedureplans`.
- **PRM decision table:** `RLM_Channel_Program_Level_Partner` remains PRM-scoped in `post_prm_pricing`.
- **Cost matrix ownership:** Workbook entry `Cost` maps to shared/default pricing decision-table ownership (existing shared Cost/CostBook decision-table assets), not PRM-local metadata.

This aligns PRM-specific pricing behavior with feature-scoped metadata while avoiding duplication of shared pricing engine assets.

**2026-05-18:** Synchronized `RLM_PRM_DISTI_Pricing_Procedure` from the active
version in source org `chrisRossPRM_may2026`. Source-org Price Adjustment
Schedule and DecisionTable IDs are represented as deploy-time placeholders,
including `__LOOKUPID_RLM_CHANNEL_PROGRAM_LEVEL_PARTNER__` for the PRM-scoped
`RLM_Channel_Program_Level_Partner` matrix.

## Field Synchronization History

**2026-05-15:** Synchronized existing PRM fields with source org `chrisRossPRM_may2026`:

- Fixed `ChannelProgramLevel.RLM_Discount_Rate__c` from type Percent → Number (scale 0)
- Added `trackHistory: false` to all 6 existing fields on ChannelProgramLevel and ChannelProgramMember
- All field definitions now match source org exactly

## Dependencies

- Revenue Cloud (Revenue Lifecycle Management) base packages
- Channel Management standard objects (ChannelProgram, ChannelProgramLevel, ChannelProgramMember)
- Experience Cloud license for Partner Central community
- Revenue Cloud Pricing User PSL for the optional `prm_pricing` extension

## Testing

Validate baseline PRM deployment:

```bash
# Deploy metadata
cci task run deploy_post_prm --org dev

# Run baseline PRM flow
cci flow run prepare_prm --org dev

# Verify fields exist
sf data query --query "SELECT EntityDefinition.QualifiedApiName, QualifiedApiName FROM FieldDefinition WHERE EntityDefinition.QualifiedApiName IN ('ChannelProgramLevel','ChannelProgramMember') AND QualifiedApiName LIKE 'RLM_%'" --target-org dev

# Load sample data
cci task run insert_quantumbit_prm_data --org dev

# Verify data loaded
sf data query --query "SELECT Name, IsPartner FROM Account WHERE Type='Partner'" --target-org dev

# Test idempotency
cci task run test_qb_prm_idempotency --org dev
```

Validate PRM pricing extension (`prm_pricing=true`):

```bash
# Run pricing extension flow directly
cci flow run prepare_prm_pricing --org dev
```

## References

- Design source: Google Sheets document (file ID: 1L3O40ManpD9ppox1CCBxw62e91YmI41yMTl5oEpbA9E)
- Source org: `chrisRossPRM_may2026` (`trailsignup.0616730547a2ce@salesforce.com`)
- Integration date: 2026-05-15

## Related Documentation

- [CCI Task/Flow Patterns](../../docs/analysis/cci-task-flow-patterns.md) - See `prepare_prm` flow details
- [SFDMU Data Plans Skill](../../.cursor/skills/sfdmu-data-plans/SKILL.md) - Data plan authoring guidance
- [Repository Integration Skill](../../.cursor/skills/repo-integration/SKILL.md) - Feature integration patterns
