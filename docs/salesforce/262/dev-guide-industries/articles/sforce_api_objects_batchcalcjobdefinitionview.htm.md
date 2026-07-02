---
page_id: sforce_api_objects_batchcalcjobdefinitionview.htm
title: BatchCalcJobDefinitionView
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_batchcalcjobdefinitionview.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: data_processing_engine_standard_object.htm
fetched_at: 2026-06-25
---

# BatchCalcJobDefinitionView

Represents the details of a Data Processing Engine definition. The
definition can also be a file-based definition that is available in your Salesforce org.
This object is available in API version 51.0 and later.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

Where possible, we changed noninclusive terms to align with our company value of
Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`describeSObjects()`, `query()`

## Fields

| Field | Details |
| --- | --- |
| CurrencyConversion | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort, Not-Nillable  Description  Specifies whether currency values must be converted when the definition is run. Possible values are:  - `Enabled` - `Disabled` - `None` |
| DataSpaceApiName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  Stores the data space API name from Data Cloud. |
| DefinitionRunMode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The execution mode of the Data Processing Engine definition.  Possible values are:  - `Batch` - `OnDemand`—On Demand  The default value is `Batch`. |
| Description | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The description of a Data Processing Engine definition. |
| DurableId | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The unique identifier for the field. Always retrieve this value before using it, as the value isn’t guaranteed to stay the same from one release to the next. Simplify queries by using this field instead of making multiple queries. |
| ExecutionPlatformObjectType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies the execution platform object type used to read, transform, and write back processes during the execution of a Data Processing Engine definition. This field is available in API version 65.0 and later.  Possible values are:  - `CalculatedInsightsObject`—Calculated Insights Object - `DataLakeObject`—Data Lake Object - `DataModelObject`—Data Model Object - `None` |
| ExecutionPlatformType | Type  Picklist  Properties  Filter, Group, Restricted picklist, Sort, Not-Nillable  Description  Specifies the platform that's used to run the Data Processing Engine definition. Possible values:  - `CDP`—Data Cloud - `CRMA`—CRM Analytics |
| InstalledPackageName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the package used to add the definition to the org. |
| IsActive | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the definition is active. |
| IsTemplate | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the definition is a template. You can make a copy of a template definition and update it based on your requirements. |
| LastModifiedBy | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The unique identifier of the user who modified the definition last. |
| ManageableState | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the definition if it’s contained in a package.  Possible values are:  - `beta`—Managed-Beta - `deleted`—Managed-Proposed-Deleted - `deprecated`—Managed-Proposed-Deprecated - `deprecatedEditable`—SecondGen-Installed-Deprecated - `installed`—Managed-Installed - `installedEditable`—SecondGen-Installed-Editable - `released`—Managed-Released - `unmanaged`—Unmanaged |
| MasterLabel | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The label of the Data Processing Engine definition. |
| Name | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the Data Processing Engine definition. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix associated with this object. Each Developer Edition organization that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the namespacePrefix\_\_componentName notation. The namespace prefix can have one of the following values:   - In Developer Edition organizations, the namespace prefix is set to the   namespace prefix of the organization for all objects that support it.   There’s an exception if an object is in an installed managed package. In   that case, the object has the namespace prefix of the installed managed   package. This field’s value is the namespace prefix of the Developer   Edition organization of the package developer. - In organizations that aren’t Developer Edition organizations,   NamespacePrefix is only set for objects that are part of an installed   managed package. There’s no namespace prefix for all other objects. |
| ProcessType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The process type of the definition.  Possible values are:  - `AccountingPeriodClosure`—Legal Entity Accounting Period   Closure—Available in API version 62.0 and later. - `AccrualsAndPayoutEngine` - `ActionableList` - `AdvancedAccountForecast` - `AutomotiveFoundation` - `BenefitManagement`—Available   in API version 61.0 and later. - `BillingSchedulesforInvoiceGeneration`—Billing Schedules   for Invoice Generation—Available in API version 62.0 and   later. - `CDPEnrichment` - `ChannelInventoryManagement`—Available in API version 63.0   and later. - `CollectionsAndRecovery` - `ContextService—Available in API   version 67.0 and later.` - `CriteriaBsdSearchAndFilter - Criteria-Based   Search And Filter` - `DataProcessingEngine -   Standard` - `DecisionMatrixDataUpload`-This value   is available only if you have Business Rules Engine enabled. - `Decisiontable`—Decision table   activation—Available in API version 62.0 and later. - `Education` - `EmployeeService`—Available in   API version 63.0 and later. - `EnergyUtilitiesSales` - `FinancialSummaryRollup`—Available in API version 63.0 and   later. - `FlexibleHierarchy` - `ForeignExchangeGainLossCalculations` - `FSCHierarchyRollUp` - `Fundraising` - `FundraisingRollups`—Available   in API version 63.0 and later. - `GeneralLedgerAccountBalancesSummary` - `InventoryBatchSearch` - `InventorySearch` - `InvoiceGeneration`—Available   in API version 62.0 and later. - `LegalEntityAccountingPeriodClosureAdvanced`—Available in   API version 63.0 and later. - `LifeSciencesCommercialTerritoryAlignment`—Available in   API version 63.0 and later. - `LifeSciencesCustomerEngagement` - `Loyalty` - `LoyaltyPartnerManagement` - `LoyaltyPointsAggregation` - `MediaAdSales` - `NetZero` - `NextGenForecasting`—Available   in API version 62.0 and later. - `PatientServicesProgram` - `PlanningAndForecasting` - `PnmRosterFileUpload`—Available in API version 62.0 and   later. - `PriceProtection`—Available in   API version 62.0 and later. - `ProductCatalogManagement`—Available in API version 63.0   and later. - `ProgramBasedBusiness` - `ProgramManagementRollups` - `Rebates` - `RebateAndAccrualManagementAdvanced` - `RecordAggregation` - `RevenueTransactionManagement`—Available in API version   63.0 and later. - `AccountingSubledger`—This   value is reserved for internal use. - `ProviderSearch`—This value is   reserved for internal use. - `Recruitment`—Available in API   version 62.0 and later. - `SalesAgreement`—Available in   API version 63.0 and later. - `StockRotation` - `UsageManagement`—Available in   API version 62.0 and later.  When Data Processing Engine is enabled for a Salesforce org, the default value is 'Standard’. Other process types may be available to you depending on your industry solution and permission sets. |
| TargetCurrencyIsoCode | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort, Not-Nillable  Description  Specifies the ISO code of the target currency used to convert currency values when the definition is run. |
