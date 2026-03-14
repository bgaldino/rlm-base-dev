# RLM_ Prefix Standardization — Full Audit Plan

> Branch: `feat/rlm-prefix-standardization`
> Goal: Rename all `RC_`, `RCA_`, and `RCB_` prefixed identifiers to `RLM_` across the entire project.

---

## Already Completed (Initial Batch)

| Old Name | New Name | Type |
|----------|----------|------|
| `unpackaged/pre/3_permissionsetgroups/RC_QB_AI` | `RLM_QB_AI` | PSG |
| `unpackaged/pre/3_permissionsetgroups/RC_RCB` | `RLM_RCB` | PSG |
| `unpackaged/pre/3_permissionsetgroups/RC_RMI` | `RLM_RMI` | PSG |
| `unpackaged/pre/3_permissionsetgroups/RC_TSO` | `RLM_TSO` | PSG |
| `unpackaged/post_utils/permissionsets/RC_Utilities` | `RLM_UtilitiesPermset` | Permset |
| `unpackaged/post_utils/permissionsets/RC_UsageManagement256PermSet` | `RLM_UsageManagementUtils` | Permset |
| `unpackaged/post_agents/permissionsets/RLM_Revenue_Cloud_Agent` | `RLM_QuotingAgent` | Permset |

---

## Conflicts & Resolutions (Review Before Executing)

### CONFLICT 1 — `RCA_Event_Trigger` is `.forceignore`-only, not a real file

**Finding:** `.forceignore` line 66 references `unpackaged/post_utils/flows/RCA_Event_Trigger.flow-meta.xml`, but this file does not exist in the repo. `RC_Event_Trigger.flow-meta.xml` is the actual file.

**Resolution:** Update `.forceignore` entry from `RCA_Event_Trigger.flow-meta.xml` → `RLM_Event_Trigger.flow-meta.xml` when renaming `RC_Event_Trigger`. No filename collision.

---

### CONFLICT 2 — `RC_Apply_Payments_on_Invoice` duplicated across three packages

**Finding:** Identical file (same MD5) exists in:
- `unpackaged/post_billing/flows/RC_Apply_Payments_on_Invoice.flow-meta.xml`
- `unpackaged/post_collections/flows/RC_Apply_Payments_on_Invoice.flow-meta.xml`
- `unpackaged/post_payments/flows/RC_Apply_Payments_on_Invoice.flow-meta.xml`

All three resolve to the same Salesforce flow in the org. This is an existing intentional pattern (each package deploys the flow independently).

**Resolution:** Rename all three to `RLM_Apply_Payments_on_Invoice.flow-meta.xml`. No collision—they're in separate directories. Update any internal `<interviewLabel>` references inside the XML.

---

### CONFLICT 3 — `RC_Home_Page_Default` in `post_tso` vs `RLM_Home_Page_Default` elsewhere

**Finding:** `unpackaged/post_tso/flexipages/RC_Home_Page_Default.flexipage-meta.xml` → rename target `RLM_Home_Page_Default`. This name already exists in `unpackaged/post_utils/flexipages/` and `unpackaged/post_quantumbit/flexipages/`, but those are separate deployment directories — no filename collision in the repo. In-org, all three deploy to the same FlexiPage record (last deploy wins by design).

**Resolution:** Rename to `RLM_Home_Page_Default.flexipage-meta.xml`. No action needed beyond the rename. Verify deployment order remains correct (post_utils/post_quantumbit before post_tso).

---

### CONFLICT 4 — `RC_MockTaxAdapter` is both Apex class metadata AND a data value in CSVs

**Finding:** `RC_MockTaxAdapter` is:
1. An Apex class (filename + class name in code)
2. A string value in tax dataset CSVs (`TaxEngine.csv`, `TaxTreatment.csv`, `TaxEngineProvider.csv`) referencing the Apex class by name
3. Referenced in `scripts/apex/createTaxEngine.apex` SOQL query by string literal

Renaming the Apex class to `RLM_MockTaxAdapter` requires updating all three places atomically, or the data load will fail (TaxEngineProvider references the class by API name).

**Resolution:** Rename class + update CSV data files + update Apex script in the same commit. Also update `datasets/sfdmu/q3/en-US/q3-tax/` CSVs which contain the same reference.

---

### CONFLICT 5 — `RC_Quote_Pricing_Procedure_Plan` is a deployed data record developer name

**Finding:** This is not just metadata — it is a **data record** (`ProcedurePlanDefinition.DeveloperName`) loaded via SFDMU. It appears in:
- `datasets/sfdmu/procedure-plans/ProcedurePlanDefinition.csv`
- `datasets/sfdmu/procedure-plans/ProcedurePlanSection.csv`
- `datasets/sfdmu/procedure-plans/ProcedurePlanDefinitionVersion.csv`
- Several `source/` CSVs
- `cumulusci.yml` YAML anchors (`procedure_plan_definition_developer_name`)

**Resolution:** Rename in all CSVs + cumulusci.yml anchors. Existing orgs with the old developer name will need the record updated or deleted+reloaded. Flag for org migration note.

---

### CONFLICT 6 — `RC_CreateOrdersFromQuote` is referenced in robot tests AND a cumulusci.yml option

**Finding:** This flow is used as a configuration value set on Revenue Settings (not just deployed metadata). It's referenced in:
- `cumulusci.yml` line 1422: `create_orders_flow: RC_CreateOrdersFromQuote` (task option)
- `robot/rlm-base/tests/setup/configure_revenue_settings.robot` line 24: variable value
- `robot/rlm-base/tests/setup/README.md`

When renamed, the Revenue Settings configuration in any existing org also needs updating (this value is stored as org configuration data, not just metadata).

**Resolution:** Rename flow + update cumulusci.yml option value + update robot variable + README. For existing orgs, re-run the revenue settings configuration task after deployment.

---

### CONFLICT 7 — `RCB_General_Ledger_Account_Assignment_Rule_Record_Page` — is the "RCB" prefix intentional?

**Finding:** Files named `RCB_General_Ledger_Account_Assignment_Rule_Record_Page.flexipage-meta.xml` exist in `post_billing` and `post_quantumbit`. Multiple app XML files reference this by content (not filename):
- `force-app/main/default/applications/RLM_Revenue_Cloud.app-meta.xml`
- `unpackaged/post_billing/applications/standard__BillingConsole.app-meta.xml`
- `unpackaged/post_collections/applications/RC_Receivables_Management.app-meta.xml`
- `unpackaged/post_tso/applications/RLM_Revenue_Cloud.app-meta.xml`
- `unpackaged/post_collections/applications/standard__CollectionConsole.app-meta.xml`

**Resolution:** Rename to `RLM_General_Ledger_Account_Assignment_Rule_Record_Page` + update all `<content>` references in the 5 app files above. **Confirm: user should verify RCB was not an intentional "Revenue Cloud Billing" namespace.**

---

## Full Rename Inventory by Category

### BATCH A — Permission Set Groups (`post_personas/`)
12 files to rename. No internal content changes needed (PSG files don't cross-reference each other by name).

| Old File | New File |
|----------|----------|
| `post_personas/permissionsetgroups/RC_Accounting_Admin` | `RLM_Accounting_Admin` |
| `post_personas/permissionsetgroups/RC_Billing_Admin` | `RLM_Billing_Admin` |
| `post_personas/permissionsetgroups/RC_Billing_Operations` | `RLM_Billing_Operations` |
| `post_personas/permissionsetgroups/RC_Credit_Memo_Operations` | `RLM_Credit_Memo_Operations` |
| `post_personas/permissionsetgroups/RC_DRO_Admin` | `RLM_DRO_Admin` |
| `post_personas/permissionsetgroups/RC_Fulfillment_Designer` | `RLM_Fulfillment_Designer` |
| `post_personas/permissionsetgroups/RC_Fulfillment_Manager` | `RLM_Fulfillment_Manager` |
| `post_personas/permissionsetgroups/RC_Product_and_Pricing_Admin` | `RLM_Product_and_Pricing_Admin` |
| `post_personas/permissionsetgroups/RC_Sales_Operations` | `RLM_Sales_Operations` |
| `post_personas/permissionsetgroups/RC_Sales_Representative` | `RLM_Sales_Representative` |
| `post_personas/permissionsetgroups/RC_Tax_Admin` | `RLM_Tax_Admin` |
| `post_personas/permissionsetgroups/RC_Usage_Designer` | `RLM_Usage_Designer` |

**cumulusci.yml updates:** Any PSG API name references in flows/tasks that assign these PSGs (search for each name in cumulusci.yml).

---

### BATCH B — Permission Sets

| Old File | New File | Notes |
|----------|----------|-------|
| `post_collections/permissionsets/RC_Collection_Plan_Activity` | `RLM_Collection_Plan_Activity` | Also referenced (commented out) in cumulusci.yml line 283 |
| `post_personas/permissionsets/RC_Custom_Sales_Rep_Perm_Set` | `RLM_Custom_Sales_Rep_Perm_Set` | |

---

### BATCH C — Flows (file rename + internal XML content update)

#### `force-app/main/default/flows/`
| Old Name | New Name | External References |
|----------|----------|---------------------|
| `RC_CreateOrdersFromQuote` | `RLM_CreateOrdersFromQuote` | cumulusci.yml line 1422; robot test; ⚠️ CONFLICT 6 |
| `RC_Refresh_Decision_Tables_By_Usage_Type` | `RLM_Refresh_Decision_Tables_By_Usage_Type` | Referenced by `RC_Account_Utilities` flow subflow call |
| `RC_Update_Asset_Pricing_Source_if_Price_Revision` | `RLM_Update_Asset_Pricing_Source_if_Price_Revision` | |

#### `unpackaged/post_approvals/flows/`
| Old Name | New Name |
|----------|----------|
| `RC_Quote_Approval_Data` | `RLM_Quote_Approval_Data` |

#### `unpackaged/post_billing/flows/`
| Old Name | New Name |
|----------|----------|
| `RC_Apply_Payments_on_Invoice` | `RLM_Apply_Payments_on_Invoice` |

#### `unpackaged/post_collections/flows/`
| Old Name | New Name |
|----------|----------|
| `RC_Apply_Payments_on_Invoice` | `RLM_Apply_Payments_on_Invoice` |
| `RC_Close_Collection_Plan_and_Associated_Cases` | `RLM_Close_Collection_Plan_and_Associated_Cases` |
| `RC_Create_Case_for_Collection` | `RLM_Create_Case_for_Collection` |
| `RC_Create_Late_Fee` | `RLM_Create_Late_Fee` |
| `RC_Create_Promise_to_Pay` | `RLM_Create_Promise_to_Pay` |
| `RC_WriteOffInvoices` | `RLM_WriteOffInvoices` |

#### `unpackaged/post_commerce/flows/`
| Old Name | New Name |
|----------|----------|
| `RC_Refresh_Commerce_Decision_Tables` | `RLM_Refresh_Commerce_Decision_Tables` |

#### `unpackaged/post_payments/flows/`
| Old Name | New Name |
|----------|----------|
| `RC_Apply_Payments_on_Invoice` | `RLM_Apply_Payments_on_Invoice` |

#### `unpackaged/post_utils/flows/`
| Old Name | New Name | Notes |
|----------|----------|-------|
| `RC_Account_Utilities` | `RLM_Account_Utilities` | Calls `RC_AccountUtilities` Apex class + `RC_Refresh_Decision_Tables_By_Usage_Type` subflow |
| `RC_AddTransactionJournalScreenFlow` | `RLM_AddTransactionJournalScreenFlow` | |
| `RC_Event_Trigger` | `RLM_Event_Trigger` | Update `.forceignore` entry too (⚠️ CONFLICT 1) |
| `RC_MonitorWorkflowServicesScreenFlow` | `RLM_MonitorWorkflowServicesScreenFlow` | |
| `RC_OrchestrateUsage` | `RLM_OrchestrateUsage` | |
| `RC_OutputUsageDataTables` | `RLM_OutputUsageDataTables` | References `RC_*__c` field names inside XML |
| `RC_Rebuild_Search_Index` | `RLM_Rebuild_Search_Index` | References `RC_RebuildSearchIndex` Apex class |
| `RC_Refresh_Asset_Decision_Tables` | `RLM_Refresh_Asset_Decision_Tables` | |
| `RC_Refresh_Pricing_Decision_Tables` | `RLM_Refresh_Pricing_Decision_Tables` | |
| `RC_Refresh_Rate_Card_Decision_Tables` | `RLM_Refresh_Rate_Card_Decision_Tables` | |
| `RC_Reset_Account` | `RLM_Reset_Account` | References `RC_AccountUtilities` Apex class |
| `RC_UpdateDecisionTables` | `RLM_UpdateDecisionTables` | Referenced in docs/TASK_EXAMPLES.md, docs/DECISION_TABLE_EXAMPLES.md, tasks/rlm_manage_decision_tables.py comments |
| `RC_Usage_Data_Tables_Concept_LS` | `RLM_Usage_Data_Tables_Concept_LS` | References `RC_*__c` field names inside XML |
| `RC_Usage_Data_Tables_Concept_TJ` | `RLM_Usage_Data_Tables_Concept_TJ` | References `RC_*__c` field names inside XML |
| `RC_Usage_Data_Tables_Concept_US` | `RLM_Usage_Data_Tables_Concept_US` | References `RC_*__c` field names inside XML |

---

### BATCH D — FlexiPages

#### `force-app/main/default/flexipages/`
| Old Name | New Name |
|----------|----------|
| `RC_Fulfillment_Step_Definition_Record_Page` | `RLM_Fulfillment_Step_Definition_Record_Page` |
| `RC_Index_Rate_Record_Page` | `RLM_Index_Rate_Record_Page` |
| `RC_Product_Usage_Resource_Record_Page` | `RLM_Product_Usage_Resource_Record_Page` |
| `RC_Quote_Line_Group_Record_Page` | `RLM_Quote_Line_Group_Record_Page` |

#### `unpackaged/post_billing/flexipages/`
| Old Name | New Name | Notes |
|----------|----------|-------|
| `RCB_General_Ledger_Account_Assignment_Rule_Record_Page` | `RLM_General_Ledger_Account_Assignment_Rule_Record_Page` | ⚠️ CONFLICT 7; update 5 app XML files |
| `RC_Billing_Schedule` | `RLM_Billing_Schedule` | |
| `RC_Billing_Schedule_Group` | `RLM_Billing_Schedule_Group` | |
| `RC_General_Ledger_Account_Assignment_Rule_Record_Page` | `RLM_General_Ledger_Account_Assignment_Rule_Record_Page` | Duplicate of RCB_ rename target — verify which is canonical |
| `RC_General_Ledger_Account_Layout` | `RLM_General_Ledger_Account_Layout` | |
| `RC_Invoice_Line_Record_Page` | `RLM_Invoice_Line_Record_Page` | |
| `RC_Receivables_Management_UtilityBar` | `RLM_Receivables_Management_UtilityBar` | |
| `RC_Usage_Entitlement_Bucket` | `RLM_Usage_Entitlement_Bucket` | |

> Note: `post_billing/RC_General_Ledger_Account_Assignment_Rule_Record_Page` and `post_billing/RCB_General_Ledger_Account_Assignment_Rule_Record_Page` appear to be two different versions of the same flexipage. Verify which is correct and whether one should be deleted.

#### `unpackaged/post_collections/flexipages/`
| Old Name | New Name |
|----------|----------|
| `RC_Billing_Account_Page` | `RLM_Billing_Account_Page` |
| `RC_Collection_Plan_Record_Page` | `RLM_Collection_Plan_Record_Page` |
| `RC_Collections_Home_Page` | `RLM_Collections_Home_Page` |

#### `unpackaged/post_constraints/flexipages/`
| Old Name | New Name |
|----------|----------|
| `RC_Asset_Action_Source_Record_Page` | `RLM_Asset_Action_Source_Record_Page` |

#### `unpackaged/post_quantumbit/flexipages/`
| Old Name | New Name | Notes |
|----------|----------|-------|
| `RCB_General_Ledger_Account_Assignment_Rule_Record_Page` | `RLM_General_Ledger_Account_Assignment_Rule_Record_Page` | ⚠️ CONFLICT 7 |
| `RC_Billing_Schedule` | `RLM_Billing_Schedule` | |
| `RC_Billing_Schedule_Group` | `RLM_Billing_Schedule_Group` | |
| `RC_General_Ledger_Account_Assignment_Rule_Record_Page` | `RLM_General_Ledger_Account_Assignment_Rule_Record_Page` | |
| `RC_General_Ledger_Account_Layout` | `RLM_General_Ledger_Account_Layout` | |
| `RC_Invoice_Line_Record_Page` | `RLM_Invoice_Line_Record_Page` | |
| `RC_Receivables_Management_UtilityBar` | `RLM_Receivables_Management_UtilityBar` | |
| `RC_Usage_Entitlement_Bucket` | `RLM_Usage_Entitlement_Bucket` | |

#### `unpackaged/post_tso/flexipages/`
| Old Name | New Name | Notes |
|----------|----------|-------|
| `RC_Home_Page_Default` | `RLM_Home_Page_Default` | ⚠️ CONFLICT 3 — verify deploy order |
| `RC_Liable_Summary_Record_Page` | `RLM_Liable_Summary_Record_Page` | |

---

### BATCH E — Custom Fields (**High Impact — touches org data schema**)

These custom field API names are referenced across flows, Apex classes, layouts, and permission sets. All references must be updated atomically.

#### `force-app/main/default/objects/Quote/fields/`
| Old Field | New Field | References |
|-----------|-----------|------------|
| `RC_Payment_Terms__c` | `RLM_Payment_Terms__c` | permsets (post_tso/RLM_QuantumBit) |
| `RC_Start_Sync__c` | `RLM_Start_Sync__c` | permsets (post_tso/RLM_QuantumBit) |

#### `unpackaged/post_approvals/objects/Quote/fields/`
| Old Field | New Field | References |
|-----------|-----------|------------|
| `RC_Approval_Level__c` | `RLM_Approval_Level__c` | flows, permsets (post_prm, post_tso), Apex (RC_QuoteApprovalController) |
| `RC_Approval_Status__c` | `RLM_Approval_Status__c` | flows, permsets (post_prm, post_tso) |

#### `unpackaged/post_approvals/objects/QuoteLineItem/fields/`
| Old Field | New Field | References |
|-----------|-----------|------------|
| `RC_Approval_Level_Calc__c` | `RLM_Approval_Level_Calc__c` | permsets (post_prm, post_tso) |
| `RC_Approval__c` | `RLM_Approval__c` | permsets (post_prm, post_tso) |

#### `unpackaged/post_billing/objects/InvoiceLine/fields/`
| Old Field | New Field | References |
|-----------|-----------|------------|
| `RC_Account__c` | `RLM_Account__c` | permsets (post_tso/RLM_QuantumBit), layouts |
| `RC_Product_Type__c` | `RLM_Product_Type__c` | permsets (post_tso/RLM_QuantumBit), layouts |

#### `unpackaged/post_utils/objects/TransactionJournal/fields/` (4 fields)
`RC_NameHyperlink__c`, `RC_QuantityUnitHyperlink__c`, `RC_ReferenceRecordHyperlink__c`, `RC_UsageResourceHyperlink__c` → `RLM_*`
References: RLM_UsageManagementUtils permset, RLM_UtilitiesPermset, flow XML (RC_Usage_Data_Tables_Concept_TJ)

#### `unpackaged/post_utils/objects/UsageBillingPeriodItem/fields/` (12 fields)
All `RC_*` → `RLM_*`
References: RLM_UsageManagementUtils permset, RLM_UtilitiesPermset, flow XML (RC_OutputUsageDataTables, RC_Usage_Data_Tables_Concept_LS)

#### `unpackaged/post_utils/objects/UsageSummary/fields/` (13 fields)
All `RC_*` → `RLM_*`
References: RLM_UsageManagementUtils permset, RLM_UtilitiesPermset, flow XML (RC_Usage_Data_Tables_Concept_US, RC_OutputUsageDataTables)

---

### BATCH F — Apex Classes (**Rename file + update class body + update all callers**)

#### `unpackaged/pre/4_tax/` (9 classes)

| Old Class | New Class | Internal Cross-references |
|-----------|-----------|---------------------------|
| `RC_MockTaxAdapter` | `RLM_MockTaxAdapter` | ⚠️ CONFLICT 4 — CSV data + createTaxEngine.apex |
| `RC_MockAppAdapter` | `RLM_MockAppAdapter` | |
| `RC_InvalidAdapter` | `RLM_InvalidAdapter` | |
| `RC_AvalaraAdapter` | `RLM_AvalaraAdapter` | Calls `RC_CalculateTaxService` |
| `RC_AvalaraJSONBuilder` | `RLM_AvalaraJSONBuilder` | Self-referencing singleton pattern |
| `RC_CalculateTaxService` | `RLM_CalculateTaxService` | Calls `RC_HttpService`, `RC_AvalaraJSONBuilder`, `RC_JsonSuccessParser`, `RC_JsonErrorParser` |
| `RC_HttpService` | `RLM_HttpService` | Self-referencing singleton pattern |
| `RC_JsonErrorParser` | `RLM_JsonErrorParser` | Self-referencing |
| `RC_JsonSuccessParser` | `RLM_JsonSuccessParser` | Self-referencing |

All 9 classes form a tightly coupled group — rename all in a single commit.

#### `unpackaged/post_utils/classes/` (2 classes)

| Old Class | New Class | Referenced by |
|-----------|-----------|---------------|
| `RC_AccountUtilities` | `RLM_AccountUtilities` | Flows: `RC_Account_Utilities`, `RC_Reset_Account` |
| `RC_RebuildSearchIndex` | `RLM_RebuildSearchIndex` | Flow: `RC_Rebuild_Search_Index` |

---

### BATCH H — Quick Actions

| Old Name | New Name | Notes |
|----------|----------|-------|
| `unpackaged/post_billing/quickActions/Invoice.RC_Apply_Payment` | `Invoice.RLM_Apply_Payment` | Update internal XML label |
| `unpackaged/post_collections/quickActions/Invoice.RC_Write_Off_Invoice` | `Invoice.RLM_Write_Off_Invoice` | |
| `unpackaged/post_utils/quickActions/Account.RC_Reset_Account` | `Account.RLM_Reset_Account` | |
| `unpackaged/post_approvals/quickActions/Quote.RC_Submit_for_Approval` | `Quote.RLM_Submit_for_Approval` | |

---

### BATCH I — Applications

| Old File | New File | Content References |
|----------|----------|--------------------|
| `unpackaged/post_collections/applications/RC_Receivables_Management.app-meta.xml` | `RLM_Receivables_Management.app-meta.xml` | Contains `RCB_General_Ledger_Account_Assignment_Rule_Record_Page` references (update as part of CONFLICT 7) |

---

### BATCH J — Global Value Sets

| Old Name | New Name |
|----------|----------|
| `unpackaged/post_approvals/globalValueSets/RC_Approval_Status` | `RLM_Approval_Status` |

Referenced by `RC_Approval_Status__c` field (BATCH E) — rename together.

---

### BATCH K — Expression Set Definitions (Procedure Plans metadata)

| Old Name | New Name | Notes |
|----------|----------|-------|
| `unpackaged/post_procedureplans/expressionSetDefinition/RC_Price_Distribution_Procedure` | `RLM_Price_Distribution_Procedure` | ⚠️ CONFLICT 5 — also in CSV data; cumulusci.yml line 1886 |
| `unpackaged/post_procedureplans/expressionSetDefinition/RC_Revenue_Management_Recalc_Procedure` | `RLM_Revenue_Management_Recalc_Procedure` | |

---

### BATCH L — Batch Calc Job Definition

| Old Name | New Name |
|----------|----------|
| `force-app/main/default/batchCalcJobDefinitions/RC_Import_Quote_Lines_With_Multi_Currency_Billing` | `RLM_Import_Quote_Lines_With_Multi_Currency_Billing` |

---

### BATCH M — Layouts

Layout filenames include the object name followed by a hyphen then the layout name. The `RC ` portion is part of the human-readable layout name.

| Old Filename | New Filename |
|--------------|--------------|
| `force-app/.../layouts/FulfillmentStepDefinition-RC Fulfillment Step Definition Layout.layout-meta.xml` | `FulfillmentStepDefinition-RLM Fulfillment Step Definition Layout.layout-meta.xml` |
| `force-app/.../layouts/ProductUsageResource-RC Product Usage Resource Layout.layout-meta.xml` | `ProductUsageResource-RLM Product Usage Resource Layout.layout-meta.xml` |
| `unpackaged/post_billing/layouts/InvoiceLine-RC Invoice Line Layout.layout-meta.xml` | `InvoiceLine-RLM Invoice Line Layout.layout-meta.xml` |
| `unpackaged/post_billing/layouts/GeneralLedgerAccount-RC General Ledger Account Layout.layout-meta.xml` | `GeneralLedgerAccount-RLM General Ledger Account Layout.layout-meta.xml` |
| `unpackaged/post_billing/layouts/UsageResource-RC Usage Resource Layout.layout-meta.xml` | `UsageResource-RLM Usage Resource Layout.layout-meta.xml` |

Also update internal `<fullName>` elements inside each layout XML to match the new filename.

---

### BATCH N — List Views & Compact Layouts

| Old Name | New Name |
|----------|----------|
| `unpackaged/post_billing/objects/Account/compactLayouts/RC_Billing_Account_Compact_Layout` | `RLM_Billing_Account_Compact_Layout` |
| `unpackaged/post_billing/objects/Invoice/listViews/RC_Failed_Invoices` | `RLM_Failed_Invoices` |
| `unpackaged/post_collections/objects/listViews/RC_All_Collection_Plans` | `RLM_All_Collection_Plans` |

---

### BATCH O — Datasets (CSV data files + export.json)

#### `datasets/sfdmu/procedure-plans/`
All references to `RC_Quote_Pricing_Procedure_Plan` (developer name in data records):
- `ProcedurePlanDefinition.csv`
- `ProcedurePlanSection.csv`
- `ProcedurePlanDefinitionVersion.csv`
- `source/ProcedurePlanDefinition_source.csv`
- `source/ProcedurePlanDefinitionVersion_source.csv`
- `source/ProcedurePlanSection_source.csv`
- `source/object-set-2/ExpressionSetDefinition_source.csv` (`RC_Price_Distribution_Procedure`)
- `source/object-set-2/ProcedurePlanOption_source.csv` (`RC_Price_Distribution_Procedure`)
- `objectset_source/object-set-2/ProcedurePlanOption.csv`

#### `datasets/sfdmu/qb/en-US/qb-tax/`
All `RC_MockTaxAdapter` references:
- `TaxEngine.csv`
- `TaxTreatment.csv`
- `TaxEngineProvider.csv`
- `source/TaxEngine_source.csv`
- `source/TaxEngineProvider_source.csv`
- `source/TaxTreatment_source.csv`

#### `datasets/sfdmu/q3/en-US/q3-tax/`
Same `RC_MockTaxAdapter` references:
- `TaxEngine.csv`
- `TaxTreatment.csv`
- `TaxEngineProvider.csv`

---

### BATCH P — Python Tasks

| File | Change |
|------|--------|
| `tasks/rlm_restore_rc_tso.py` | Update all hardcoded `RC_TSO` filename strings to `RLM_TSO`; consider renaming class `RestoreRCTSO` → `RestoreRLMTSO` |
| `tasks/rlm_manage_decision_tables.py` | Update comments referencing `RC_UpdateDecisionTables` flow (lines 5, 9) |

---

### BATCH Q — cumulusci.yml

| Location | Current Value | New Value |
|----------|---------------|-----------|
| Line 283 | `#- RC_Collection_Plan_Activity` | `#- RLM_Collection_Plan_Activity` |
| Line 452 | `RC_Quote_Pricing_Procedure_Plan` (anchor) | `RLM_Quote_Pricing_Procedure_Plan` |
| Line 453 | `RC_Quote_Pricing_Procedure_Plan` (anchor) | `RLM_Quote_Pricing_Procedure_Plan` |
| Line 461 | `RC_Quote_Pricing_Procedure_Plan` (anchor) | `RLM_Quote_Pricing_Procedure_Plan` |
| Line 710 | description mentions `RC_TSO` → `RLM_TSO` | Already correct (`RLM_TSO`) — verify |
| Line 1422 | `create_orders_flow: RC_CreateOrdersFromQuote` | `RLM_CreateOrdersFromQuote` |
| Line 1882 | description mentions `RC_Price_Distribution_Procedure` | Update description text |
| Line 1886 | `version_full_names: RC_Price_Distribution_Procedure_V1` | `RLM_Price_Distribution_Procedure_V1` |
| PSG/permset API name lists | All `RC_` PSG names in `rlm_tso_psg_api_names`, etc. | Update to `RLM_` |

---

### BATCH R — Robot Framework Tests

| File | Change |
|------|--------|
| `robot/rlm-base/tests/setup/configure_revenue_settings.robot` | Line 24: `RC_CreateOrdersFromQuote` → `RLM_CreateOrdersFromQuote` |
| `robot/rlm-base/tests/setup/README.md` | Update `CREATE_ORDERS_FLOW` default value in docs |

---

### BATCH S — Documentation

| File | References to Update |
|------|---------------------|
| `docs/constraints_setup.md` | `RC_Asset_Action_Source_Record_Page`, `RC_CreateOrdersFromQuote` |
| `docs/TASK_EXAMPLES.md` | `RC_UpdateDecisionTables`, `RC_Account_Utilities` |
| `docs/DECISION_TABLE_EXAMPLES.md` | `RC_UpdateDecisionTables` |
| `datasets/procedure-plans/README.md` | `RC_Price_Distribution_Procedure`, `RC_Revenue_Management_Recalc_Procedure`, `RC_Quote_Pricing_Procedure_Plan` |
| `datasets/sfdmu/qb/en-US/qb-tax/README.md` | `RC_MockTaxAdapter` |

---

### BATCH T — `.forceignore`

| Change |
|--------|
| Line 66: `unpackaged/post_utils/flows/RCA_Event_Trigger.flow-meta.xml` → `unpackaged/post_utils/flows/RLM_Event_Trigger.flow-meta.xml` |

---

## Recommended Execution Order

Execute in this order to minimize forward-reference failures:

1. **BATCH E** — Custom fields first (all downstream references depend on new field API names)
2. **BATCH J** — Global value set `RC_Approval_Status` → `RLM_Approval_Status`
3. **BATCH F** — Apex classes (tax suite as one atomic commit; utils+approvals as another)
4. **BATCH G** — VF Pages (depend on Apex class name)
5. **BATCH C** — Flows (reference Apex class names and field API names)
6. **BATCH D** — FlexiPages (reference flow names)
7. **BATCH H** — Quick Actions
8. **BATCH I** — Applications (reference flexipage names — resolve CONFLICT 7 first)
9. **BATCH A** — PSGs (post_personas batch)
10. **BATCH B** — Remaining permsets
11. **BATCH K** — Expression set definitions (metadata files)
12. **BATCH L** — Batch calc job
13. **BATCH M** — Layouts
14. **BATCH N** — List views / compact layouts
15. **BATCH O** — Dataset CSVs (update data values to match renamed metadata)
16. **BATCH P** — Python tasks
17. **BATCH Q** — cumulusci.yml
18. **BATCH R** — Robot tests
19. **BATCH S** — Documentation
20. **BATCH T** — `.forceignore`

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Files to rename (filename change) | ~155 |
| Files needing content-only updates (no rename) | ~40 |
| Distinct Salesforce metadata types affected | 16 |
| Conflicts requiring manual decision | 7 |
| Data CSV files with embedded developer names | ~15 |

---

## Open Questions for Review

1. **CONFLICT 7**: Is `RCB_` an intentional "Revenue Cloud Billing" namespace that should become `RLM_` or stay as `RCB_`?
2. **`post_billing/RC_General_Ledger_Account_Assignment_Rule_Record_Page` vs `post_billing/RCB_General_Ledger_Account_Assignment_Rule_Record_Page`**: Two versions of the same flexipage. Which is canonical? Should one be deleted?
3. **Org migration**: For existing non-scratch orgs (e.g., TSO), custom field renames (`RC_*__c` → `RLM_*__c`) require a migration approach. Is in-place rename via Metadata API acceptable, or is a data migration script needed?
4. **`RC_Quote_Pricing_Procedure_Plan`** (CONFLICT 5): For existing orgs, this requires deleting and re-loading the procedure plan, or using a data migration script to update `DeveloperName`. Confirm acceptable approach.
