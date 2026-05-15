# Partner Relationship Management (PRM) Metadata

This directory contains Partner Relationship Management metadata for Revenue Cloud Base Foundations, including custom fields, flows, pricing components, permission sets, and Experience Cloud site configuration.

## Overview

The PRM feature enables partner and distributor pricing workflows through:
- Partner account relationships and hierarchies
- Channel program management with discount tiers
- Quote-level distributor pricing fields
- Quote line item distributor and partner net pricing
- Decision tables for channel program evaluation
- Context definitions for sales transaction pricing
- Partner Central community site (rlm1)

## Contents

### Custom Fields

**Account (2 fields):**
- `RLM_Primary_Reseller__c` - Lookup to Account representing the primary reseller
- `RLM_Primary_Distributor__c` - Lookup to Account representing the primary distributor

**Quote (1 field):**
- `RLM_Distributor_Account__c` - Lookup to Account for the distributor on this quote

**QuoteLineItem (3 fields):**
- `RLM_Distributor_Discount_Percent__c` - Percent field for distributor discount
- `RLM_Distributor_Unit_Price__c` - Currency field for distributor unit price
- `RLM_Partner_Net_Total_Price__c` - Currency field for partner net total price

**ChannelProgramLevel (3 fields):**
- `RLM_Deal_Expiration_Days__c` - Number field for deal expiration period
- `RLM_Discount_Rate__c` - Number field (0 decimal places) for discount rate
- `RLM_Minimum_Deal_Size__c` - Currency field for minimum deal size threshold

**ChannelProgramMember (3 fields):**
- `RLM_Adjustment_Type__c` - Text field (255 chars) for adjustment type
- `RLM_Adjustment_Value__c` - Number field (2 decimal places) for adjustment value
- `RLM_Discount_Rate__c` - Number field (2 decimal places) for discount rate

### Flows (2)

- `RLM_Update_Channel_Program_Member.flow` - Updates channel program member records
- `RLM_Create_New_Quote.flow` - Creates new quote with PRM pricing context

### Pricing Components

**Decision Tables (1):**
- `Channel_Program_Level_Partner.decisionTable` - Evaluates channel program level and partner criteria

**Context Definitions (1):**
- `RLM_SalesTransactionContext.contextDefinition` - Maps PRM fields to sales transaction context for pricing engine
  - Maps `RLM_Distributor_Account__c` and `PartnerAccount__c` to SalesTransaction
  - Maps `RLM_Distributor_Unit_Price__c`, `RLM_Distributor_Discount_Percent__c`, `RLM_Partner_Net_Total_Price__c` to SalesTransactionItem

### Permission Sets (2)

- `RLM_PRM.permissionset-meta.xml` - Grants read/edit access to all 12 PRM custom fields (6 on channel objects, 6 on quote/account objects)
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

This task is automatically included in the `prepare_prm` flow:

```bash
cci flow run prepare_prm --org <org-alias>
```

The `prepare_prm` flow includes 9 steps:
1. Create Partner Central community
2. Patch network metadata (email placeholder)
3. Deploy post_prm metadata
4. Revert network metadata
5. Publish Partner Central community
6. Deploy sharing rules
7. Assign permission sets
8. Load QuantumBit PRM data
9. Apply context definitions

## Data Loading

Sample partner data is loaded via SFDMU:

```bash
cci task run insert_quantumbit_prm_data --org <org-alias>
```

The data plan loads:
- Pass 1: Partner Accounts, Channel Programs, Channel Program Levels
- Pass 2: Enable IsPartner on Accounts, Channel Program Members

**Note:** The Account fields `RLM_Primary_Reseller__c` and `RLM_Primary_Distributor__c` are included in the query but populated as empty in the sample data.

## Feature Flags

Enable PRM in `cumulusci.yml`:

```yaml
project_config:
  project__custom__:
    prm: true                    # Core PRM feature
    prm_exp_bundle: true         # Experience Cloud site content
```

## Known Limitations & Follow-up Required

### ⚠️ Pricing Procedures - REQUIRES FOLLOW-UP

The design spreadsheet references the following pricing components that could **not be retrieved** via Metadata API:

**Pricing Procedures/Recipes:**
- `PRM_DISTI_Pricing_Procedure`
- `RLM_DefaultPricingProcedure`
- `RLM_Price_Distribution_Procedure`

**Price Adjustment Matrices:**
- "Cost" adjustment matrix
- "Channel Program Level Partner" adjustment matrix

**Status:** These components exist in the source org `chrisRossPRM_may2026` but:
1. `PricingProcedure` metadata type is not supported by the Metadata API in API v66.0
2. `PriceAdjustmentMatrix` metadata type is not supported by the Metadata API in API v66.0
3. Retrieved `PricingRecipe` metadata type only returned standard recipes (`NGPDefaultRecipe`, `CommerceDefaultRecipe`), not the custom procedures listed above

**Possible Reasons:**
- These may be custom Apex classes or helper methods (search for `PRM_DISTI_Pricing_Procedure` in Apex classes)
- These may be OmniStudio Integration Procedures (use different retrieval mechanism)
- These may be GraphQL calculation procedures embedded in another metadata type
- These may be manually configured in the UI and not backed by metadata

**Required Follow-up Actions:**
1. Investigate the actual metadata type for these procedures in the source org
2. Determine if they are Apex classes, OmniStudio IPs, or UI-only configurations
3. Retrieve using the appropriate mechanism (Apex retrieval, OmniStudio export, etc.)
4. Document any manual configuration steps if not metadata-backed
5. Update this README and the deployment documentation once resolved

**Impact:** The PRM feature will deploy and function with custom fields and flows, but **pricing automation may not work** until these procedures are added. Manual pricing may be required in the interim.

**Tracking:** This limitation was documented on 2026-05-15 during integration of the PRM design spreadsheet from `chrisRossPRM_may2026` org.

## Field Synchronization History

**2026-05-15:** Synchronized existing PRM fields with source org `chrisRossPRM_may2026`:
- Fixed `ChannelProgramLevel.RLM_Discount_Rate__c` from type Percent → Number (scale 0)
- Added `trackHistory: false` to all 6 existing fields on ChannelProgramLevel and ChannelProgramMember
- All field definitions now match source org exactly

## Dependencies

- Revenue Cloud (Revenue Lifecycle Management) base packages
- Channel Management standard objects (ChannelProgram, ChannelProgramLevel, ChannelProgramMember)
- Experience Cloud license for Partner Central community
- Revenue Cloud Pricing User PSL (for pricing context/procedures)

## Testing

Validate PRM deployment:

```bash
# Deploy metadata
cci task run deploy_post_prm --org dev

# Verify fields exist
sf data query --query "SELECT QualifiedApiName FROM FieldDefinition WHERE EntityDefinition.QualifiedApiName IN ('Account','Quote','QuoteLineItem') AND QualifiedApiName LIKE 'RLM_%'" --target-org dev

# Load sample data
cci task run insert_quantumbit_prm_data --org dev

# Verify data loaded
sf data query --query "SELECT Name, RLM_Primary_Reseller__c, RLM_Primary_Distributor__c FROM Account WHERE Type='Partner'" --target-org dev

# Test idempotency
cci task run test_qb_prm_idempotency --org dev
```

## References

- Design source: Google Sheets document (file ID: 1L3O40ManpD9ppox1CCBxw62e91YmI41yMTl5oEpbA9E)
- Source org: chrisRossPRM_may2026 (trailsignup.0616730547a2ce@salesforce.com)
- Integration date: 2026-05-15
- Branch: feature/prm

## Related Documentation

- [CCI Task/Flow Patterns](../../docs/analysis/cci-task-flow-patterns.md) - See `prepare_prm` flow details
- [SFDMU Data Plans Skill](../../.cursor/skills/sfdmu-data-plans/SKILL.md) - Data plan authoring guidance
- [Repository Integration Skill](../../.cursor/skills/repo-integration/SKILL.md) - Feature integration patterns
