# Project Analysis: Revenue Cloud Foundations & Distill

> **Document Type:** Living Reference
> **Last Updated:** 2026-02-27
> **Scope:** Comprehensive technical reference for both projects — capabilities, architecture, inventories
>
> **Part of:** [Revenue Cloud Engineering Platform](revenue-cloud-platform.md)

---

## Table of Contents

### Part 1 — Revenue Cloud Foundations
1. [Overview & Positioning](#11-overview--positioning)
2. [Tech Stack & Prerequisites](#12-tech-stack--prerequisites)
3. [Project Structure](#13-project-structure)
4. [Feature Flags](#14-feature-flags)
5. [Scratch Org Configurations](#15-scratch-org-configurations)
6. [Flows & Sub-Flows](#16-flows--sub-flows)
7. [Custom Python Tasks](#17-custom-python-tasks)
8. [Salesforce Metadata](#18-salesforce-metadata)
9. [Data Plans](#19-data-plans)
10. [Constraints & CML](#110-constraints--cml)
11. [Context Definitions](#111-context-definitions)
12. [Robot Framework Automation](#112-robot-framework-automation)
13. [Scripts & Utilities](#113-scripts--utilities)
14. [Documentation Index](#114-documentation-index)

### Part 2 — Distill
1. [Overview & Positioning](#21-overview--positioning)
2. [Tech Stack & Dependencies](#22-tech-stack--dependencies)
3. [Architecture Overview](#23-architecture-overview)
4. [The Four Engines](#24-the-four-engines)
5. [Agent Architecture & Sub-Agent Pattern](#25-agent-architecture--sub-agent-pattern)
6. [REST API — Complete Reference](#26-rest-api--complete-reference)
7. [Database Layer](#27-database-layer)
8. [Configuration System](#28-configuration-system)
9. [CLI Interface & Slash Commands](#29-cli-interface--slash-commands)
10. [LLM Integration & Providers](#210-llm-integration--providers)

---

# Part 1 — Revenue Cloud Foundations

## 1.1 Overview & Positioning

**Revenue Cloud Foundations** is an enterprise CumulusCI automation framework for building and configuring Salesforce Revenue Cloud (Revenue Lifecycle Management) orgs from scratch. It answers the question: *"How do I stand up a correctly configured Revenue Cloud org, with the right data, permissions, and settings, repeatably across any org type?"*

- **Salesforce Release:** 260 (Spring '26 GA)
- **API Version:** 66.0
- **Branch strategy:** `main` targets Release 260 GA; `260-dev` is the active development branch
- **Automation coverage:** ~95% — only Salesforce CLI authentication and Dev Hub configuration remain manual

**What makes it distinctive:**
- 50+ feature flags control conditional deployment of 25+ metadata bundles and 11 data plans
- Three data shape families (QB, Q3, MFG) with locale variants (en-US, ja)
- SFDMU v5 composite key patterns for idempotent data loading
- Polymorphic ID resolution for Constraint Model Library (CML) imports
- Browser automation via Robot Framework for Salesforce Setup UI toggles that have no Metadata API equivalent

---

## 1.2 Tech Stack & Prerequisites

| Component | Version | Purpose |
|---|---|---|
| CumulusCI | 4.0.0+ | Core automation framework |
| Salesforce CLI | 2.x+ | Org authentication, metadata push/pull |
| SFDMU | 5.0.0+ | Data loading (v4 no longer supported) |
| Python | 3.8+ | Custom task runtime |
| Robot Framework | Latest | Browser-based UI automation |
| SeleniumLibrary | Latest | Robot keyword library |
| webdriver-manager | Latest | Auto-manages ChromeDriver |
| urllib3 | 2.6.3+ | Selenium 3.x compatibility patch |
| Node.js | LTS | LWC Jest testing |
| prettier | 3.x | Code formatting (Apex, LWC, XML, YAML) |

**Installation (recommended):**
```bash
pipx install cumulusci
pipx inject cumulusci robotframework robotframework-seleniumlibrary \
  webdriver-manager "urllib3>=2.6.3"
```

**Validation:**
```bash
cci task run validate_setup   # checks all prerequisites, auto-fixes SFDMU if needed
```

---

## 1.3 Project Structure

```
revenue-cloud-foundations/
├── force-app/main/default/         # Core Salesforce metadata (125 XML files)
│   ├── classes/                    # 8 Apex classes
│   ├── lwc/                        # Lightning Web Components
│   ├── contextDefinitions/         # 10 context definition files
│   ├── permissionsets/             # Permission sets
│   ├── flexipages/                 # Lightning pages
│   ├── staticresources/
│   ├── objects/                    # Standard object customizations
│   ├── settings/                   # Org settings
│   ├── groups/ & roles/
│   └── standardValueSets/
│
├── unpackaged/                     # Conditional metadata (498 XML files)
│   ├── pre/                        # Pre-deployment bundles (5 bundles)
│   │   ├── 1_settings/
│   │   ├── 2_settings/
│   │   ├── 3_permissionsetgroups/
│   │   ├── 4_tax/
│   │   └── 5_decisiontables/
│   └── post_*/                     # Feature-specific post-deployment bundles (20+)
│       ├── post_agents/            ├── post_approvals/    ├── post_billing/
│       ├── post_billing_id_settings/                      ├── post_billing_template_settings/
│       ├── post_clm/              ├── post_commerce/      ├── post_constraints/
│       ├── post_context/          ├── post_docgen/        ├── post_guidedselling/
│       ├── post_payments/         ├── post_payments_settings/
│       ├── post_personas/         ├── post_prm/           ├── post_procedureplans/
│       ├── post_quantumbit/       ├── post_rmi/           ├── post_scratch/
│       ├── post_sharing/          ├── post_tso/           ├── post_utils/
│       └── post_visualization/
│
├── tasks/                          # 24 custom CumulusCI Python task modules
├── robot/rlm-base/                 # Robot Framework automation
│   ├── tests/setup/                # 3 test suites
│   ├── resources/                  # Shared keywords + WebDriverManager patch
│   └── variables/
│
├── datasets/                       # All data plans and reference data
│   ├── constraints/                # CML expression set data + blobs
│   ├── context_plans/              # Context definition manifests
│   └── sfdmu/                      # SFDMU data plans by shape/locale
│       ├── qb/en-US/ & ja/         ├── q3/en-US/   ├── mfg/en-US/
│       ├── procedure-plans/        ├── scratch_data/
│       └── reconcile/
│
├── scripts/
│   ├── apex/                       # 24 anonymous Apex scripts
│   ├── bash/
│   ├── soql/
│   └── *.py                        # Python utility scripts
│
├── orgs/                           # 20 scratch org definitions
├── docs/                           # Documentation (10+ guides)
└── cumulusci.yml                   # Main CCI config (2,386+ lines)
```

---

## 1.4 Feature Flags

All flags are set under `project.custom` in `cumulusci.yml` and drive conditional task/flow execution throughout `prepare_rlm_org`.

### Data Shape Flags
| Flag | Default | Controls |
|---|---|---|
| `qb` | `true` | QuantumBit product dataset (PCM, pricing, product images) |
| `q3` | `false` | Q3 multi-currency data variant |

### Module Flags
| Flag | Default | Controls |
|---|---|---|
| `billing` | `true` | Billing terms, schedules, legal entities, GL accounts |
| `payments` | `true` | Payments site, flows, settings |
| `tax` | `true` | Tax policies, treatments, engine |
| `dro` | `true` | Dynamic Revenue Orchestration fulfillment plans |
| `clm` | `true` | Contract Lifecycle Management metadata |
| `clm_data` | `false` | CLM reference data loading |
| `docgen` | `true` | Document Generation templates and settings |
| `agents` | `false` | Agentforce agents and settings |
| `prm` | `true` | Partner Relationship Management |
| `prm_exp_bundle` | `false` | PRM experience bundle publishing |
| `commerce` | `false` | Commerce features |
| `constrains` | `true` | Constraints Engine metadata |
| `constraints_data` | `true` | CML constraint model import |
| `guidedselling` | `false` | Guided Selling assessment scripts |
| `procedureplans` | `true` | Procedure Plan definitions and sections |
| `visualization` | `false` | Flow visualization components |
| `breconfig` | `false` | BRE reconfiguration |

### Data Flags
| Flag | Default | Controls |
|---|---|---|
| `rating` | `true` | Usage rating design-time data |
| `rates` | `true` | Rate card entries |
| `ramps` | `true` | Ramp configurations |

### Org Type Flags
| Flag | Default | Controls |
|---|---|---|
| `tso` | `false` | Trialforce Source Org metadata and permissions |
| `qbrix` | `false` | xDO base (QBrix) compatibility |
| `refresh` | `false` | Data refresh mode |
| `sharingsettings` | `false` | Sharing rules deployment |

### Deployment Flags
| Flag | Default | Controls |
|---|---|---|
| `calmdelete` | `true` | CALM delete operations |
| `einstein` | `true` | Einstein/AI permission sets |
| `approvals` | `true` | Approval workflow metadata |

---

## 1.5 Scratch Org Configurations

20 scratch org definition files in `orgs/`:

| File | Purpose |
|---|---|
| `dev.json` | Standard development scratch org |
| `dev_enhanced.json` | Development with enhanced features |
| `beta.json` | Beta features testing |
| `dev_preview.json` | Preview release features |
| `dev_previous.json` | Previous release testing |
| `dev_datacloud.json` | Data Cloud feature testing |
| `test-sb0.json` | Test sandbox (SB0) variant |
| `dev-sb0.json` | Dev sandbox (SB0) variant |
| `tfid.json` | Base Trial Force ID org |
| `tfid-dev.json` | TFID development |
| `tfid-cdo.json` | TFID CDO variant |
| `tfid-cdo-rlm.json` | TFID CDO with RLM |
| `tfid-sdo.json` | TFID SDO variant |
| `tfid-sdo-lite.json` | TFID SDO lite |
| `tfid-ido-tech-SB0.json` | TFID IDO tech (SB0) |
| `tfid-ido-tech-R2.json` | TFID IDO tech (R2) |
| `tfid-qb-tso.json` | QuantumBit TSO |
| `tfid-enable.json` | Enablement org |
| *(additional variants)* | — |

---

## 1.6 Flows & Sub-Flows

### Main Orchestration Flow: `prepare_rlm_org` (29 steps)

| Step | Sub-flow / Task | Condition | Purpose |
|---|---|---|---|
| 1 | `prepare_core` | Always | PSL/PSG, context defs, rule libraries, settings cleanup |
| 2 | `prepare_decision_tables` | Scratch only | Activate decision tables |
| 3 | `prepare_expression_sets` | Scratch only | Deploy expression sets (draft) |
| 4 | `create_partner_central` | `prm` | PRM partner central |
| 5 | `create_payments_webhook` | `payments` | Payments webhook setup |
| 6 | `deploy_full` | Always | Full metadata deployment |
| 7 | `prepare_price_adjustment_schedules` | Scratch | Activate PAS |
| 8 | `prepare_scratch` | Scratch + not `tso` | Insert scratch-only seed data |
| 9 | `prepare_payments` | Always | Deploy payments site and settings |
| 10 | `prepare_quantumbit` | Always | QB metadata, permissions, CALM delete |
| 11 | `prepare_product_data` | `qb` or `q3` | Load PCM + product images |
| 12 | `prepare_pricing_data` | `qb` | Load pricing data |
| 13 | `prepare_docgen` | `docgen` | Doc Gen library, toggles, metadata |
| 14 | `prepare_dro` | `dro` + (`qb` or `q3`) | DRO data with dynamic user |
| 15 | `prepare_tax` | `tax` + (`qb` or `q3`) | Tax engine, data, activation |
| 16 | `prepare_billing` | `billing` + (`qb` or `q3`) | Billing load, activation, ID settings |
| 17 | `prepare_clm` | `clm` + `clm_data` | CLM data loading |
| 18 | `prepare_rating` | `rating` + `rates` + (`qb` or `q3`) | Rating + rates data, activation |
| 19 | `activate_and_deploy_expression_sets` | Always | Re-deploy Draft→Active via XPath |
| 20 | `prepare_tso` | `tso` | TSO permissions, metadata |
| 21 | `prepare_procedureplans` | `procedureplans` | PPD + sections via Connect API |
| 22 | `prepare_prm` | `prm` | Community publish, sharing rules |
| 23 | `prepare_agents` | `agents` | Agentforce agents and settings |
| 24 | `prepare_constraints` | `constrains` | Metadata, CML import, activation |
| 25 | `prepare_guidedselling` | `guidedselling` + `qb` | Guided selling data + metadata |
| 26 | `prepare_visualization` | `visualization` | Visualization components |
| 27 | `configure_revenue_settings` | Always | Robot-driven revenue settings config |
| 28 | `reconfigure_pricing_discovery` | Scratch + not `tso` | Fix pricing discovery procedure |
| 29 | `refresh_all_decision_tables` | Always | Sync pricing, refresh all DT categories |

### Other Top-Level Flows
| Flow | Purpose |
|---|---|
| `run_qb_extracts` | Runs all 9 QB extraction tasks |
| `run_qb_idempotency_tests` | Runs all 9 QB idempotency tests (load twice, verify no dupes) |
| `extract_rating` | Extract rating + rates data |
| `analyze_org_drift` | *(Distill integration — see distill-integration.md)* |

---

## 1.7 Custom Python Tasks

All 24 modules in `tasks/`:

### Data Management
| Task Class | Module | Purpose |
|---|---|---|
| `LoadSFDMUData` | `rlm_sfdmu.py` (38KB) | Generic SFDMU v5 loader — simulation mode, object sets, dynamic user replacement |
| `InsertQuantumbitPCMData` | `rlm_sfdmu.py` | Load PCM product catalog |
| `InsertQuantumbitPricingData` | `rlm_sfdmu.py` | Load pricing data |
| `InsertQuantumbitBillingData` | `rlm_sfdmu.py` | Load billing data (3-pass) |
| `InsertQuantumbitTaxData` | `rlm_sfdmu.py` | Load tax data |
| `InsertQuantumbitDROData` | `rlm_sfdmu.py` | Load DRO data with dynamic user |
| `InsertQuantumbitRatingData` | `rlm_sfdmu.py` | Load rating data (2-pass) |
| `InsertQuantumbitRatesData` | `rlm_sfdmu.py` | Load rate card data |
| `InsertProcedurePlansData` | `rlm_sfdmu.py` | Load procedure plan sections (2-pass) |
| *(extract variants)* | `rlm_sfdmu.py` | 9 extraction tasks (SFDMU → CSV) |
| *(idempotency tests)* | `rlm_sfdmu.py` | 9 idempotency tests |

### Constraint Model Library (CML)
| Task Class | Module | Purpose |
|---|---|---|
| `ExportCML` | `rlm_cml.py` | Export ESC records + ESDV blob from org |
| `ImportCML` | `rlm_cml.py` | Import with polymorphic ID resolution, dry-run mode |
| `ValidateCML` | `rlm_cml.py` | Validate CSV structure + ESC association coverage |

### Metadata Management
| Task Class | Module | Purpose |
|---|---|---|
| `ManageDecisionTables` | `rlm_manage_decision_tables.py` | List/query/refresh/activate/deactivate DTs by category |
| `RefreshDTRating` | — | Refresh rating DTs |
| `RefreshDTRatingDiscovery` | — | Refresh rating discovery DTs |
| `RefreshDTDefaultPricing` | — | Refresh default pricing DTs |
| `RefreshDTPricingDiscovery` | — | Refresh pricing discovery DTs |
| `RefreshDTAsset` | — | Refresh asset DTs |
| `RefreshDTCommerce` | — | Refresh commerce DTs |
| `ManageExpressionSets` | `rlm_manage_expression_sets.py` | List/activate/deactivate expression set versions |
| `ManageFlows` | `rlm_manage_flows.py` | List/activate/deactivate flows |
| `ManageTransactionProcessingTypes` | `rlm_manage_transaction_processing_types.py` | List/upsert/delete TPT records |

### Context Definitions
| Task Class | Module | Purpose |
|---|---|---|
| `ManageContextDefinition` | `rlm_context_service.py` (52KB) | Modify context definitions via Context Service API |
| `ExtendStandardContext` | `rlm_extend_stdctx.py` (11KB) | Extend 11 standard RLM contexts with custom attributes |

### Setup & Configuration
| Task Class | Module | Purpose |
|---|---|---|
| `ValidateSetup` | `rlm_validate_setup.py` (20KB) | Check Python/CCI/SF CLI/SFDMU/Robot versions; auto-fix SFDMU |
| `CleanupSettingsForDev` | `rlm_cleanup_settings.py` (25KB) | Remove unsupported settings for scratch orgs |
| `AssignPermissionSetLicenses` | — | Assign PSLs (with retry) |
| `AssignPermissionSetGroupsTolerant` | `rlm_assign_permission_set_groups.py` | Assign PSGs (with missing-permission tolerance) |
| `RecalculatePermissionSetGroups` | `rlm_recalculate_permission_set_groups.py` | Recalc PSGs with status polling |
| `EnableDocumentBuilderToggle` | `rlm_enable_document_builder_toggle.py` | Robot-driven Document Builder toggle |
| `EnableConstraintsSettings` | `rlm_enable_constraints_settings.py` | Robot-driven constraints setup |
| `ConfigureRevenueSettings` | `rlm_configure_revenue_settings.py` | Robot-driven revenue settings |
| `ExcludeActiveDecisionTables` | `rlm_exclude_active_decision_tables.py` | Move active DTs to `.skip` before deploy |
| `DeployBillingIdSettings` | — | XPath-transform ID resolution for billing fields |
| `ReconfigurePricingDiscovery` | `rlm_reconfigure_expression_set.py` | Fix pricing discovery procedure |
| `CreateProcedurePlanDefinition` | `rlm_create_procedure_plan_def.py` | Create PPD + inactive Version via Connect API |
| `SyncPricingData` | `rlm_sync_pricing_data.py` | Pricebook entry sync |
| `EnsurePricingSchedules` | `rlm_repair_pricing_schedules.py` | Validate pricing schedules pre-deploy |
| `RestoreRCTSO` | `rlm_restore_rc_tso.py` | Restore Revenue Cloud TSO metadata |
| `DistillCaptureDrift` | `rlm_distill_capture.py` *(planned)* | Optional Distill integration — org drift capture |
| `GenerateBaselineManifest` | `rlm_generate_baseline_manifest.py` *(planned)* | Generate shape_manifest.json from export.json files |

---

## 1.8 Salesforce Metadata

### force-app (Core — 125 files)

| Type | Count | Key Examples |
|---|---|---|
| Apex Classes | 8 | `RLM_PlaceQuoteModel`, `RLM_PlaceOrderModel`, `RLM_QuoteModelUtility`, `RLM_DFOTenantProvisioningCallout`, `RLM_DetermineDROSourceType` |
| Context Definitions | 10 | All 11 standard RLM contexts (see §1.11) |
| Permission Sets | Multiple | `RLM_QuantumBit` (primary) |
| Settings | Multiple | `LargeQuotesandOrdersForRlm.settings` |
| Flexipages | Multiple | Standard Lightning app pages |
| Standard Objects Modified | 7 | Order, Asset, Quote, QuoteLineItem, Product2, OrderItem, FulfillmentOrderLineItem |

### unpackaged/ (Conditional — 498 files)

**Pre-deployment bundles (5):** Sequential numbered deployment — settings, PSGs, tax metadata, decision table scaffolding.

**Post-deployment bundles (20+):**

| Bundle | Feature Flag | Key Contents |
|---|---|---|
| `post_agents` | `agents` | Agentforce agents, flows, settings |
| `post_approvals` | `approvals` | Approval workflow metadata |
| `post_billing` | `billing` | Billing flexipages, toggles |
| `post_billing_id_settings` | `billing` | XPath-transformed ID field settings |
| `post_billing_template_settings` | `billing` | Invoice template toggle cycle |
| `post_clm` | `clm` | Contract Lifecycle Management |
| `post_commerce` | `commerce` | Commerce features |
| `post_constraints` | `constrains` | Constraints Engine classes, triggers, UI |
| `post_context` | Always | Extended context definitions |
| `post_docgen` | `docgen` | Document Generation templates |
| `post_guidedselling` | `guidedselling` | Guided selling scripts |
| `post_payments` | `payments` | Payments site and flows |
| `post_payments_settings` | `payments` | Payments configuration |
| `post_personas` | Always | Persona profiles and permission sets |
| `post_prm` | `prm` | Partner Relationship Management |
| `post_procedureplans` | `procedureplans` | Procedure plan definitions |
| `post_quantumbit` | `qb` | QB-specific UI, themes, transforms |
| `post_rmi` | Always | RLM Margin Intelligence permission sets |
| `post_scratch` | Scratch only | Scratch org-only features |
| `post_sharing` | `sharingsettings` | Sharing rules |
| `post_tso` | `tso` | Trialforce Source Org metadata |
| `post_utils` | Always | Utility flows and classes |
| `post_visualization` | `visualization` | Flow visualization components |

---

## 1.9 Data Plans

Full inventory of all SFDMU data plans. See [datasets-reorganization.md](datasets-reorganization.md) for folder structure proposal.

### QB Shape — English US (`qb/en-US/`)

| Plan | Objects | Passes | Composite Keys | Feature Flags | Status |
|---|---|---|---|---|---|
| `qb-pcm` | 28 | 1 | 10 | `qb` | Active (v5) |
| `qb-pricing` | 16 | 1 (objectSet) | 8 | `qb` | Active (v5) |
| `qb-product-images` | 1 | 2 | 0 | `qb` | Active (v5) |
| `qb-billing` | 11 | 3 | 3 (`$$` notation) | `qb`, `billing` | Active (v5) |
| `qb-tax` | 6 | 2 | 1 | `qb`, `tax` | Active (v5) |
| `qb-dro` | 13 | 1 | 1 | `qb`, `dro` | Active (v5) |
| `qb-rating` | 14 | 2 | 3 (`$$` notation) | `qb`, `rating` | Active (v5) |
| `qb-rates` | 5 | 1 | 3 | `qb`, `rates` | Active (v5) |
| `qb-transactionprocessingtypes` | 1 | 1 | 0 | `qb` | Active (v5) |
| `qb-accounting` | ~6 | 1 | — | `qb` | Reference export |
| `qb-clm` | ~8 | 1 | — | `qb`, `clm` | Active |
| `qb-guidedselling` | ~5 | 2 | — | `qb`, `guidedselling` | Active |
| `qb-constraints-component` | ~4 | — | — | `qb`, `constrains` | Export-only |
| `qb-constraints-exported` | ~4 | — | — | `qb`, `constrains` | Blob-based export |

**Total qb/en-US:** 95 Salesforce objects, 154 SOQL queries, 29 composite external IDs (13 using `$$` notation)

### QB Shape — Japanese (`qb/ja/`)

| Plan | Objects | Differences from en-US | Status |
|---|---|---|---|
| `qb-pcm` | 28 | `ProductSellingModelOption` externalId uses 2 fields instead of 3 | Active (v5) |
| `qb-pricing` | ~14 | Simplified composite keys, fewer excluded objects | Active (v5) |

**Coverage gap:** No Japanese variants for billing, tax, DRO, rating, rates, CLM, guided selling.

### Q3 Shape — English US (`q3/en-US/`)

| Plan | Objects | Key Difference from QB | Status |
|---|---|---|---|
| `q3-billing` | ~11 | Simplified external IDs, 1 pass vs 3 | Pending v5 migration |
| `q3-dro` | ~13 | Q3 product model | Pending v5 migration |
| `q3-multicurrency` | 40+ | Largest plan — PCM + multi-currency pricing combined | Pending v5 migration |
| `q3-rates` | ~5 | Q3 rate card variant | Pending v5 migration |
| `q3-rating` | ~14 | Q3 usage rating | Pending v5 migration |
| `q3-tax` | ~6 | Q3 tax variant | Pending v5 migration |

### MFG Shape — English US (`mfg/en-US/`)

| Plan | Objects | Purpose | Status |
|---|---|---|---|
| `mfg-configflow` | 2 | ProductConfigurationFlow + assignments | Draft |
| `mfg-constraints-p` | — | Manufacturing constraint data | Draft |
| `mfg-constraints-prc` | — | Manufacturing PRC constraints | Draft |
| `mfg-multicurrency` | — | MFG multi-currency support | Draft |

### Cross-Shape Plans (`_shared/` — proposed)

| Plan | Objects | Passes | Purpose |
|---|---|---|---|
| `procedure-plans` | 3 (Readonly × 2, Upsert × 1) | 2 | Procedure Plan sections and options |
| `scratch_data` | 2 | 1 | Basic Account + Contact test seed data |

---

## 1.10 Constraints & CML

The Constraint Model Library (CML) pipeline is separate from SFDMU. It handles Expression Set definitions and their associated binary blobs (`.ffxblob` files).

**Current location:** `datasets/constraints/qb/`
**Proposed location:** `datasets/sfdmu/qb/en-US/constraints/` (see [datasets-reorganization.md](datasets-reorganization.md))

### Constraint Datasets

| Dataset | ESC Records | Products | PRC Entries | Blob |
|---|---|---|---|---|
| `QuantumBitComplete` | 43 | 22 | 21 | `ESDV_QuantumBitComplete_V1.ffxblob` |
| `Server2` | 81 | 41 | 40 | `ESDV_Server2_V1.ffxblob` |

### CML CSV Files (per dataset)
- `ExpressionSet.csv`
- `ExpressionSetConstraintObj.csv`
- `ExpressionSetDefinitionVersion.csv`
- `ExpressionSetDefinitionContextDefinition.csv`
- `Product2.csv`
- `ProductClassification.csv`
- `ProductRelatedComponent.csv`

### CML Pipeline
1. **Export** (`export_cml` task): Queries ESC records, exports CSVs + ESDV blob from source org
2. **Import** (`import_cml` task): Resolves polymorphic IDs (Product2/ProductClassification/PRC via prefix detection), imports CSVs, injects blob
3. **Validate** (`validate_cml` task): Checks CSV structure, ESC association coverage, relationship integrity

---

## 1.11 Context Definitions

11 standard RLM contexts are extended via the Context Service API (not Metadata API). Managed by `rlm_context_service.py` (52KB) and `rlm_extend_stdctx.py` (11KB).

| Context | Mapping |
|---|---|
| `RLM_AssetContext` | `AssetEntitiesMapping` |
| `RLM_SalesTransactionContext` | `QuoteEntitiesMapping` |
| `RLM_ProductDiscoveryContext` | `ProductDiscoveryMapping` |
| `RLM_CommerceCartContext` | `CommerceCartMapping` |
| `RLM_BillingContext` | `BSGEntitiesMapping` |
| `RLM_FulfillmentAssetContext` | `FulfillAssetEntitiesMapping` |
| `RLM_ContractsContext` | `OppToCntrPersistenceMapping` |
| `RLM_ContractsExtractionContext` | `DocExtrctPersistenceMapping` |
| `RLM_CollectionPlanSegmentCtx` | `CollectionPlanContextMapping` |
| `RLM_RateManagementContext` | `DefaultUsageMapping` |
| `RLM_RatingDiscoveryContext` | `CatalogMapping` |

**Context plan manifests** live in `datasets/context_plans/` and drive the `manage_context_definition` task.

---

## 1.12 Robot Framework Automation

Used for Salesforce Setup UI configuration where no Metadata API equivalent exists.

### Test Suites (`robot/rlm-base/tests/setup/`)

| Suite | Keywords | Purpose |
|---|---|---|
| `enable_document_builder.robot` | 3 | Document Builder toggle, Document Templates Export toggle, Design Document Templates toggle |
| `enable_constraints_settings.robot` | 3 | Default Transaction Type, Asset Context selection, Constraints Engine toggle |
| `configure_revenue_settings.robot` | 4 | Pricing Procedure, Usage Rating, Instant Pricing toggle, Create Orders Flow |

### Infrastructure
- **`SetupToggles.robot`** — shared keywords for browser navigation and toggle enabling
- **`SetupVariables.robot`** — Setup page URLs
- **`WebDriverManager.py`** — patches `RemoteConnection._timeout` at import for urllib3 2.x compatibility
- **Authentication:** `sf org open --url-only` for Salesforce CLI session injection
- **Browser:** Chrome headless (set `BROWSER=firefox` for alternative)

### Prerequisites
```bash
pipx inject cumulusci robotframework robotframework-seleniumlibrary \
  webdriver-manager "urllib3>=2.6.3"
```

---

## 1.13 Scripts & Utilities

### Anonymous Apex (`scripts/apex/` — 24 scripts)

| Script | Purpose |
|---|---|
| `activateBillingRecords.apex` | Activate billing policies/treatments |
| `activateDecisionTables.apex` | Activate all decision tables |
| `activateDefaultPaymentTerm.apex` | Set default payment term |
| `activatePriceAdjustmentSchedules.apex` | Activate PAS records |
| `activateRatingRecords.apex` | Activate rating records (incl. PUR ordering) |
| `activateTaxRecords.apex` | Activate tax policies/treatments |
| `cleanupRatingRecords.apex` | Clean up rating records for re-load |
| `createDRORuleLibrary.apex` | Create DRO rule library |
| `createDocgenTemplateLibrary.apex` | Create Document Gen template library |
| `createRuleLibrary.apex` | Create pricing rule library |
| `createTaxEngine.apex` | Create and configure tax engine |
| `deactivateDecisionTables.apex` | Deactivate all active DTs |
| `deleteDraftBillingRecords.apex` | Clean up draft billing records |
| `deleteQbRatesData.apex` | Delete rate card data for re-load |
| *(10 more)* | DT queries, rating cleanup, schedule management |

### Python Utilities (`scripts/`)

| Script | Purpose |
|---|---|
| `post_process_extraction.py` | Add composite `$$` key columns to extracted CSVs for re-import |
| `compare_sfdmu_content.py` | Compare SFDMU data plan versions |
| `compare_sfdmu_extractions.py` | Compare extraction results across runs |
| `reconcile_detail_qb_tax_billing_rating_rates.py` | Multi-plan reconciliation |

---

## 1.14 Documentation Index

| File | Size | Contents |
|---|---|---|
| **[README.md](../README.md)** | 48KB, 890 lines | Complete setup, prerequisites, quick start, feature flags, workflows |
| **[docs/constraints_setup.md](constraints_setup.md)** | — | `prepare_constraints` flow order and deployment phases |
| **[docs/DECISION_TABLE_EXAMPLES.md](DECISION_TABLE_EXAMPLES.md)** | — | DT management task comprehensive examples |
| **[docs/TASK_EXAMPLES.md](TASK_EXAMPLES.md)** | — | Flow and expression set task examples |
| **[docs/context_service_utility.md](context_service_utility.md)** | — | Context Service API usage and plan examples |
| **[docs/sfdmu_composite_key_optimizations.md](sfdmu_composite_key_optimizations.md)** | — | SFDMU v5 migration, idempotency, composite key analysis |
| **[docs/rca_rcb_unique_id_fields.md](rca_rcb_unique_id_fields.md)** | — | Unique ID field analysis for RLM objects |
| **[docs/TOOLING_OPPORTUNITIES.md](TOOLING_OPPORTUNITIES.md)** | — | Spring '26 feature analysis and new tooling opportunities |
| `docs/CML_User_Guide.pdf` | 5.4MB | Salesforce CML documentation |
| **[datasets/constraints/README.md](../datasets/constraints/README.md)** | 417 lines | CML export/import/validate architecture |
| **[robot/rlm-base/tests/setup/README.md](../robot/rlm-base/tests/setup/README.md)** | — | Robot Framework setup automation for UI toggles |
| **[postman/README_V260_ANALYSIS.md](../postman/README_V260_ANALYSIS.md)** | — | v260 API analysis — 129 endpoints, implementation status |
| **[docs/distill-integration.md](distill-integration.md)** | — | Distill integration specification (see Part 2) |
| **[docs/datasets-reorganization.md](datasets-reorganization.md)** | — | Datasets folder reorganization proposal |
| **[docs/revenue-cloud-platform.md](revenue-cloud-platform.md)** | — | Platform overview for Revenue Cloud Foundations + Distill + Aegis |

---

---

# Part 2 — Distill

## 2.1 Overview & Positioning

**Distill** (`sf-industries/distill`) is an AI-powered Salesforce customization migration platform built exclusively on the Claude Agent SDK. It answers the question: *"What customizations exist in a Salesforce codebase, what do they mean for the business, and how do I translate them to a target platform?"*

- **Python:** 3.10–3.12
- **LLM:** Claude Sonnet 4.5 / Haiku 4.5 — accessed via **Vertex AI on GCP** (provisioned through Embark). No direct Anthropic API or Bedrock.
- **Storage:** SQLite (primary — relational project/migration data), ChromaDB (vector — configured in `base.yaml`), NetworkX (graph — configured in `base.yaml`)
- **Interface:** Interactive CLI (`./distill start`), TUI (Textual), REST API (Web mode — future)

**What makes it distinctive:**
- Clean Architecture: Core (domain/services) → Controllers → UI — core has zero UI dependencies
- Claude Agent SDK used exclusively — no custom Anthropic client wrapper
- Six specialized agents, each owning only the tools it needs; three are currently implemented
- Support for multi-entity schema mappings (1:1, 1:N, N:1, N:M) via DataMapperAgent
- Pluggable storage, event bus, and plugin system for extensibility

---

## 2.2 Tech Stack & Dependencies

### Core
| Package | Version | Role |
|---|---|---|
| `claude-agent-sdk` | Latest | LLM orchestration and MCP tool management (exclusive LLM interface) |
| `pydantic` | 2.x+ | Type-safe configuration (v2 with validators) |
| `sqlalchemy` | 2.0+ | ORM for SQLite relational data |
| `chromadb` | Configured | Vector embeddings — configured in `base.yaml` with `sentence-transformers/all-MiniLM-L6-v2`; code path integration in progress |
| `networkx` | Configured | Dependency graph — configured in `base.yaml` as graph backend; code path integration in progress |

### LLM Access
| Model | Access Path | Used By |
|---|---|---|
| `claude-sonnet-4-5@20250929` | Vertex AI via GCP/Embark | Orchestration |
| `claude-haiku-4-5@20251001` | Vertex AI via GCP/Embark | CodeSuggestion, DataMapper agents |
| `GEMINI_API_KEY` | Google AI direct | Gemini adapter (optional) |

> **Note:** LLM access requires a GCP project provisioned via [Embark](https://embark.sfdcbt.net/). No direct Anthropic API key or AWS Bedrock configuration is used.

### UI & CLI
| Package | Role |
|---|---|
| `textual` | TUI framework (Salesforce-themed terminal app) |
| `typer` | CLI framework |
| `rich` | Console output formatting |
| `prompt_toolkit` | Interactive prompts |

### Optional Salesforce
| Package | Role |
|---|---|
| `simple-salesforce` | Salesforce REST API client |
| `sfdx-simple` | SFDX CLI wrapper |

---

## 2.3 Architecture Overview

Distill follows **Clean Architecture** — dependencies point inward only; core has zero UI dependencies.

```
distill/
├── main.py                         # Entry point (./distill start)
├── src/distill/
│   ├── core/                       # Pure business logic — NO UI imports
│   │   ├── domain/
│   │   │   ├── models.py           # Domain models (Project, ExecutionPlan, etc.)
│   │   │   └── protocols.py        # Service/repository interfaces
│   │   └── services/               # Service implementations
│   │       ├── project_service.py
│   │       ├── llm_service.py
│   │       ├── ingestion_service.py    # (planned)
│   │       └── analysis_service.py     # (planned)
│   │
│   ├── infrastructure/             # Data persistence
│   │   └── repositories/
│   │       ├── sqlite_repository.py    # Production storage
│   │       └── in_memory_repository.py # Test storage
│   │
│   ├── controllers/                # Adapters: UI ↔ core services
│   │   ├── project_controller.py
│   │   └── migration_controller.py
│   │
│   ├── agents/                     # Claude Agent SDK agent implementations
│   │   ├── base_agent.py           # BaseAgent protocol
│   │   ├── codesuggestion/         # ✅ Implemented
│   │   │   ├── codesuggestion_main_agent.py
│   │   │   ├── file_migration_agent.py
│   │   │   ├── feature_migration_agent.py
│   │   │   └── modification_sub_agent.py
│   │   ├── datamapper/             # ✅ Implemented
│   │   │   └── datamapper_agent.py
│   │   └── deployment/             # ✅ Implemented
│   │       ├── deployment_agent.py
│   │       └── deployment_agent_datamapper.py
│   │
│   ├── ui/                         # Presentation layer only
│   │   ├── tui/                    # Textual TUI (Salesforce-themed)
│   │   ├── cli/                    # Typer CLI
│   │   └── web/                    # FastAPI REST (future)
│   │
│   ├── orchestrator/               # AgentOrchestrator (Claude SDK management)
│   ├── config/                     # Layered YAML config (base/dev/prod/test)
│   ├── storage/                    # Storage abstraction + factory
│   ├── llm/                        # Claude SDK client (config accessor only)
│   ├── logging/                    # Loguru + Rich output
│   ├── plugins/                    # Plugin system
│   └── events/                     # Event bus
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

---

## 2.4 Agent Architecture

Distill's agent layer registers **four agents** with the `AgentOrchestrator`, which manages Claude SDK sessions, tool aggregation, and routing. Three are full standalone agents; a fourth (`DeploymentAgentDataMapper`) is a DataMapper-aware deployment variant. Three additional agents are planned.

### Implemented Agents

#### CodeSuggestionAgent ✅

Migrates Apex classes and triggers from a source org to a target platform.

**Model:** `claude-haiku-4-5@20251001` (Vertex AI)
**Pattern:** Single-tier — agent calls tools directly with no sub-agents

**Primary tool:** `run_file_migration(file_path)`
- Takes a `.cls` or `.trigger` file path
- Outputs migrated code ready for the target org

> ⚠️ **Implementation note:** `run_file_migration` internally uses **Gemini** (hardcoded), not Claude. The orchestration shell runs on `claude-haiku-4-5@20251001`, but the actual code translation logs `"⚠️ Anthropic/Claude Vertex DISABLED - Gemini is HARDCODED for all migrations"`. The `llm_provider` defaults to `"gemini"` regardless of config. Integration consumers should account for Gemini being the effective translation engine at the tool layer.

**Sub-agents (supporting):**
- `file_migration_agent` — per-file migration
- `feature_migration_agent` — feature-wide migration via dependency traversal
- `modification_sub_agent` — human-in-loop modification requests

**Integration note:** This is the only Distill agent available for integration with Foundations today. See Phase 1 in [distill-integration.md](distill-integration.md).

---

#### DataMapperAgent ✅

Interactive entity and field-level mapping between source and target schemas. Supports all cardinalities (1:1, 1:N, N:1, N:M).

**Model:** `claude-haiku-4-5` (Vertex AI)
**Pattern:** Single-tier — conversational, human-driven

**Tools:**
- `update_entity_mapping(legacy_entity, modern_entity, column_mappings)` — simple 1:1 mapping
- `create_advanced_mapping(legacy_entities, modern_entities, column_mappings)` — multi-entity (1:N, N:1, N:M)
- `update_column_mapping(legacy_entity, legacy_column, modern_mappings)` — per-field updates

**Usage:** User says "map `AML_Vehicle__c` to `Vehicle, Asset, Product2`" — agent calls the appropriate tool. Interactive only; not designed for programmatic automation.

---

#### DeploymentAgent ✅

Deploys migrated code and schema changes to a Salesforce org.

**Model:** `claude-sonnet-4-5@20250929` (Vertex AI)
**Tools:** `Read`, `Grep`, `Glob`, `Write`, `Edit`, `Bash` (Claude Code built-in tools)

> ⚠️ **Context requirement:** DeploymentAgent relies exclusively on Claude Code built-in tools. It is only operable within an active **Claude Code session** — it cannot be invoked from a CCI subprocess, standard Python process, or any non-Claude Code runtime. Supports Apex only; requires interactive org path/URL input from the user.

#### DeploymentAgentDataMapper ✅

A DataMapper-aware deployment variant registered alongside DeploymentAgent in `main_agents.py`. Handles deployment of mapped entities after schema mapping has been completed via DataMapperAgent.

**Files:** `deployment_agent.py`, `deployment_agent_datamapper.py`

---

### Planned Agents (Not Yet Registered)

| Agent | Purpose | Module Status | Required For |
|---|---|---|---|
| **IngestionAgent** | Ingest org metadata from a retrieved codebase | `src/distill/insights/` exists (with `api.py`, `pipeline.py`, full pipeline subdirs) — agent registration pending | Automated org analysis (Phase 3 of Foundations integration) |
| **AnalysisAgent** | Feature/capability extraction, drift detection, impact analysis | `src/distill/analysis/` exists (with `ingestion/`, `parsing/`, `llm/`, `models.py`) — agent registration pending | Automated drift reporting (Phase 4 of Foundations integration) |
| **ProjectAgent** | Project initialization, workspace setup, configuration management | Not yet present | Full project lifecycle management |

> **Note:** `AnalyseFeature` tools are available in the current build via slash commands (per `main_agents.py` comment), suggesting partial analysis functionality exists even before a formal AnalysisAgent registration. When formal agent registration is complete, the Foundations integration can move from manually-triggered Apex migration to fully automated drift detection. See [distill-integration.md](distill-integration.md) §8 for the phased roadmap.

---

## 2.5 Agent Architecture & Sub-Agent Pattern

Distill uses a strict **tool ownership** model to prevent LLM tool confusion:

| Role | Tools Available | Purpose |
|---|---|---|
| **Orchestrators** | `AskUserQuestion` only | Route work to sub-agents; do not directly execute |
| **Sub-agents** | Focused execution tools | Perform specific operations (file migration, mapping, etc.) |

This physical separation ensures orchestrators cannot accidentally call wrong execution tools. Sub-agents are specialized and stateless between invocations.

**Human-in-the-loop:** Controlled via `agent.enable_human_in_loop: true` in config. Critical operations surface for approval before execution.

---

## 2.6 REST API — Complete Reference

Base URL: configurable (default `http://localhost:8000`)
Spec: `GET /openapi.json` | UI: `GET /docs`

### Read Endpoints

| Method | Path | Purpose | Key Params |
|---|---|---|---|
| `GET` | `/health` | Health check | — |
| `GET` | `/api/projects` | List all projects | — |
| `GET` | `/api/projects/{id}` | Get project details | — |
| `GET` | `/api/projects/{id}/vectorization-status` | Vectorization progress | — |
| `GET` | `/api/analysis/{id}/summary` | Analysis stats + completion | `mode`, `repo_type` |
| `GET` | `/api/analysis/{id}/features` | Business feature inventory | `mode`, `repo_type` |
| `GET` | `/api/datamapper/{id}/schema/{type}` | Get schema | `type`: source/target/mapping |
| `GET` | `/api/migration/{id}/records` | Migration history | `metadata_type` |
| `GET` | `/api/migration/file-content` | Get file content | `path` |
| `GET` | `/api/migration/child-content` | Get child file contents | `parent_record_id` |
| `GET` | `/api/workspace/active` | Active project info | — |
| `GET` | `/export` | Export tar archive | `format`, `name` |

### Trigger Endpoints (Long-Running)

| Method | Path | Required Body | Optional Body |
|---|---|---|---|
| `POST` | `/api/analysis/run` | `project_id`, `source_path` | `repo_type`, `skip_stages[]` |
| `POST` | `/api/projects/{id}/vectorize` | — | `scope` |
| `POST` | `/api/datamapper/run` | `project_id` OR `legacy_paths[]`+`modern_paths[]` | `output_dir` |
| `POST` | `/api/feature-mapping/run` | `source`, `target`, `entity_map` | `top_n`, `min_confidence`, `use_llm`, `output_dir` |
| `POST` | `/api/migration/run` | `project_id`, `user_request`, `target_platform` | — |

### Key Response Schemas

**Project object:**
```json
{
  "id": "<uuid>",
  "project_name": "<string>",
  "domain": "<string>",
  "status": "active|in_progress|completed|failed|archived",
  "vectorization_complete": false,
  "source_folder_location": "<string>",
  "target_folder_location": "<string>",
  "customization_folder_location": "<string|null>"
}
```

**Feature object:**
```json
{
  "business_feature_id": "<string>",
  "name": "<string>",
  "description": "<string>",
  "entities": ["Product2", "PricebookEntry"],
  "operations": ["C", "R", "U", "D"],
  "files": ["<file_path>"],
  "ui_components": ["<component_id>"],
  "mode": "fast|thorough"
}
```

**Known gap:** No `POST /api/projects` endpoint — projects must be created via Distill CLI (`/configure`). See `distill-integration.md §4.3`.

---

## 2.7 Database Layer

### SQLite Tables (SQLAlchemy ORM)

| Table | Key Fields | Purpose |
|---|---|---|
| `projects` | `id` (UUID), `project_name`, `domain`, `status`, `source_folder_location` | Project registry |
| `migration_records` | `id`, `project_id` (FK), `source_file_path`, `migrated_file_path`, `parent_record_id` (self-ref) | Migration history |
| `workspace_config` | `active_project_id`, `source_path`, `target_path` | Active workspace state |
| `mapping_runs` | `run_id`, `total_mappings`, `exact_matches`, `avg_confidence` | DataMapper run history |
| `feature_mappings` | `source_feature_id`, `target_feature_id`, `confidence`, `match_type`, `justification` | Feature mapping results |

### DuckDB Tables (Insights Pipeline — per-project)

> ⚠️ **Validation note:** `base.yaml` configures `sqlite` as the primary storage backend with no DuckDB section present. The `src/distill/insights/` module exists and is active (`enable_insights: true` in config), but its specific storage backend requires verification. The table below reflects the originally designed schema and may not reflect current implementation.

| Table | Key Fields | Purpose |
|---|---|---|
| `insights_artifacts` | `artifact_id`, `type`, `name`, `file_path`, `is_entry_point`, `entry_point_tier` | Code artifact inventory |
| `insights_business_features` | `business_feature_id`, `name`, `description`, `entities_json`, `operations_json`, `files_json` | Extracted business features |
| `insights_flows` | `flow_id`, `entry_point_id`, `full_path_json`, `entities_accessed_json`, `summary` | Execution flow traces |
| `insights_entities` | — | Entity access tracking |
| `insights_calls` | — | Cross-artifact call graph |

### ChromaDB Collections
- Code embeddings using `sentence-transformers/all-MiniLM-L6-v2`
- Separate collections per project for source, target, and customization codebases
- Used by CodeSuggestion engine for RAG-first discovery

---

## 2.8 Configuration System

Layered YAML configuration (each layer overrides the previous):
1. `config/base.yaml` — defaults
2. `config/{env}.yaml` — environment overrides (dev/test/prod)
3. `config/local.yaml` — local overrides (gitignored)
4. Environment variables (`DISTILL_*` prefix)

### Key Configuration Sections

```yaml
llm:
  provider: anthropic              # anthropic | openai | gemini
  model: claude-sonnet-4-5@20250929
  fast_model: claude-haiku-4-5@20251001
  max_tokens: 4096

storage:
  backend: sqlite
  database.url: sqlite:///./output/distill.db
  chroma.path: ./output/chroma
  chroma.embedding_function: sentence-transformers/all-MiniLM-L6-v2

agent:
  permission_mode: bypassPermissions
  enable_human_in_loop: true

logging:
  level: INFO
  format: pretty
  log_file: ./output/distill.log
```

---

## 2.9 CLI Interface & Slash Commands

**Entry point:** `./distill start`

| Command | Category | Purpose |
|---|---|---|
| `/configure` | Project | Configure project (name, domain, source/target paths) |
| `/configure-customization` | Project | Configure custom code directory |
| `/config` | Project | Show current configuration |
| `/project-status` | Project | Show background processing status |
| `/workspace` | Project | Show active project configuration |
| `/list-projects` | Project | List all projects |
| `/show-project` | Project | Show project details |
| `/run-datamapper` | Analysis | Execute schema mapping pipeline |
| `/merge-customization` | Analysis | Merge customizations into mapping |
| `/parse-schema` | Analysis | Parse Salesforce schema files |
| `/distill-customization` | Analysis | Full customization analysis |
| `/migrate-metadata` | Migration | Migrate Salesforce metadata |
| `/find` | Migration | Semantic code discovery (Claude-powered) |
| `/vectorize` | Vectorization | Vectorize project for RAG |
| `/vectorize-status` | Vectorization | Show vectorization progress |
| `/vectorize-resume` | Vectorization | Resume incomplete vectorization |
| `/insights [fast\|thorough]` | Insights | Run 10-stage Insights pipeline |
| `/dashboard` | UI | Launch Flask web dashboard |
| `/help` | Utility | Show all commands |
| `/exit` / `/quit` | Utility | Exit session |

---

## 2.10 LLM Integration & Providers

### Model Selection Strategy

| Use Case | Model | Rationale |
|---|---|---|
| Complex migration tasks / orchestration | `claude-sonnet-4-5` | High accuracy for code translation and agent coordination |
| Fast classification/routing | `claude-haiku-4-5` | Low latency for high-volume decisions; wraps `run_file_migration` tool call |
| **Code migration tool (`run_file_migration`)** | **Gemini (hardcoded)** | **`run_file_migration` always routes through Gemini regardless of config — see §2.4 note** |
| Large context analysis | `gemini-2.5-pro` | Large context window for big codebases |

### RAG Pipeline (CodeSuggestion)

```
User request (file path)
        ↓
ChromaDB vector search     ← sentence-transformers/all-MiniLM-L6-v2
        ↓
NetworkX knowledge graph   ← dependency traversal
        ↓
DataMapper field mappings  ← entity-level context
        ↓
Merged context prompt      → Claude Sonnet → migrated code
```

### Vertex AI Support
Distill runs Claude orchestration models through Google Vertex AI (`claude_vertex_adapter.py`). Note that `run_file_migration` — the primary CodeSuggestion tool — uses Gemini (hardcoded), not Claude Vertex. See §2.4 for the implementation note.
