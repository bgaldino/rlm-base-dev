---
page_id: tooling_api_objects_batchcalcjobdefinition.htm
title: BatchCalcJobDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_batchcalcjobdefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: data_processing_engine_setup_object.htm
fetched_at: 2026-06-25
---

# BatchCalcJobDefinition

Represents a Data Processing Engine (DPE) definition. This object
is available in API version 51.0 and later.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

Where possible, we changed noninclusive terms to align with our company value of
Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`,
`update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

| Field | Details |
| --- | --- |
| BatchJobDefinitionId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The unique identifier of the associated batch job definition.  This is a relationship field.  Relationship Name  BatchJobDefinition  Relationship Type  Lookup  Refers To  BatchJobDefinition |
| CurrencyConversion | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort, Not-Nillable  Description  Specifies whether currency values must be converted when the definition is run. Possible values are:  - `Enabled` - `Disabled` - `None` |
| DataSpaceApiName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The Data Space API name from Data Cloud. |
| DefinitionRunMode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The execution mode of the Data Processing Engine definition.  Possible values are:  - `Batch` - `OnDemand`—This value is   reserved for internal use.  The default value is `Batch`. |
| DeveloperName | Type  string  Properties  Filter, Group, Sort  Description  The developer name of the Data Processing Engine definition. |
| DoesGenAllFailedRecords | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the error file includes a complete list of all failed writeback records (`true`) or not (`false`). The default value is `false`, and only the first instance of a failure is recorded in the error file. If set to `true`, all failed records are recorded in the error file for the writeback node. Available in API version 65.0 and later. |
| ExecutionPlatformObjectType | Type  Picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Required. The execution platform object type that's used during the read, transform, and writeback process for the Data Processing Engine definition. Possible values are:  - `CalculatedInsightsObject` - `DataLakeObject` - `DataModelObject` - `None`  Available in API version 65.0 and later. |
| ExecutionPlatformType | Type  Picklist  Properties  Filter, Group, Restricted picklist, Sort, Not-Nillable  Description  Specifies the platform that's used to run the Data Processing Engine definition. Possible values:  - `CDP`—Data Cloud - `CORE`—This value is reserved   for internal use. - `CRMA`—CRM Analytics |
| FullName | Type  string  Properties  Create, Group, Nillable  Description  The name of the Data Processing Engine definition.  Query this field only if the query result contains no more than one record. Otherwise, an error is returned. If more than one record exists, use multiple queries to retrieve the records. This limit protects performance. |
| IsTemplate | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether this is a template Data Processing Engine definition. |
| Language | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The language in which this Data Processing Engine definition is created. |
| ManageableState | Type  ManageableState enumerated list  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package:  - `beta` - `deleted` - `deprecated` - `deprecatedEditable` - `installed` - `installedEditable` - `released` - `unmanaged` |
| MasterLabel | Type  string  Properties  Filter, Group, Sort  Description  The label of the Data Processing Engine definition. |
| Metadata | Type  complexvalue  Properties  Create, Nillable, Update  Description  Data Processing Engine definition's metadata.  Query this field only if the query result contains no more than one record. Otherwise, an error is returned. If more than one record exists, use multiple queries to retrieve the records. This limit protects performance. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix associated with this object. Each Developer Edition organization that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `namespacePrefix__componentName` notation. The namespace prefix can have one of the following values:   - In Developer Edition organizations, the namespace prefix is set to the   namespace prefix of the organization for all objects that support it.   There’s an exception if an object is in an installed managed package. In   that case, the object has the namespace prefix of the installed managed   package. This field’s value is the namespace prefix of the Developer   Edition organization of the package developer. - In organizations that aren’t Developer Edition organizations,   NamespacePrefix is only set for objects that are   part of an installed managed package. There’s no namespace prefix for all   other objects. |
| ProcessType | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. The process type for which the Data Processing Engine definition is created.  Possible values are:  - `AccountingPeriodClosure`—Legal Entity Accounting Period   Closure—Available in API version 62.0 and later. - `AccrualsAndPayoutEngine` - `ActionableList` - `AdvancedAccountForecast` - `AutomotiveFoundation` - `BenefitManagement`—Available   in API version 61.0 and later. - `BillingSchedulesforInvoiceGeneration`—Billing Schedules   for Invoice Generation—Available in API version 62.0 and   later. - `CDPEnrichment` - `ChannelInventoryManagement`—Available in API version 63.0   and later. - `CollectionsAndRecovery` - `ContextService—Available in API   version 67.0 and later.` - `CriteriaBsdSearchAndFilter - Criteria-Based   Search And Filter` - `DataProcessingEngine -   Standard` - `DecisionMatrixDataUpload`-This value   is available only if you have Business Rules Engine enabled. - `Decisiontable`—Decision table   activation—Available in API version 62.0 and later. - `Education` - `EmployeeService`—Available in   API version 63.0 and later. - `EnergyUtilitiesSales` - `FinancialSummaryRollup`—Available in API version 63.0 and   later. - `FlexibleHierarchy` - `ForeignExchangeGainLossCalculations` - `FSCHierarchyRollUp` - `Fundraising` - `FundraisingRollups`—Available   in API version 63.0 and later. - `GeneralLedgerAccountBalancesSummary` - `InventoryBatchSearch` - `InventorySearch` - `InvoiceGeneration`—Available   in API version 62.0 and later. - `LegalEntityAccountingPeriodClosureAdvanced`—Available in   API version 63.0 and later. - `LifeSciencesCommercialTerritoryAlignment`—Available in   API version 63.0 and later. - `LifeSciencesCustomerEngagement` - `Loyalty` - `LoyaltyPartnerManagement` - `LoyaltyPointsAggregation` - `MediaAdSales` - `NetZero` - `NextGenForecasting`—Available   in API version 62.0 and later. - `PatientServicesProgram` - `PlanningAndForecasting` - `PnmRosterFileUpload`—Available in API version 62.0 and   later. - `PriceProtection`—Available in   API version 62.0 and later. - `ProductCatalogManagement`—Available in API version 63.0   and later. - `ProgramBasedBusiness` - `ProgramManagementRollups` - `Rebates` - `RebateAndAccrualManagementAdvanced` - `RecordAggregation` - `RevenueTransactionManagement`—Available in API version   63.0 and later. - `AccountingSubledger`—This   value is reserved for internal use. - `ProviderSearch`—This value is   reserved for internal use. - `Recruitment`—Available in API   version 62.0 and later. - `SalesAgreement`—Available in   API version 63.0 and later. - `StockRotation` - `UsageManagement`—Available in   API version 62.0 and later.  When Data Processing Engine is enabled for a Salesforce org, the default value is 'Standard’. Other process types may be available to you depending on the licenses available in your org. |
| TargetCurrencyIsoCode | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort, Not-Nillable  Description  Specifies the ISO code of the target currency used to convert currency values when the definition is run. |
