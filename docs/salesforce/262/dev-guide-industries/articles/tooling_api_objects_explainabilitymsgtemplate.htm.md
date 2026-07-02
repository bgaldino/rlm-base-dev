---
page_id: tooling_api_objects_explainabilitymsgtemplate.htm
title: ExplainabilityMsgTemplate
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_explainabilitymsgtemplate.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_explainer_bre_tooling_objects_parent.htm
fetched_at: 2026-06-25
---

# ExplainabilityMsgTemplate

Represents the template that contains the decision explanation
message for a specified element type. This object is available in API version 56.0 and
later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=industries_reference)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `search()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

| Field | Details |
| --- | --- |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The unique name for the ExplainabilityMsgTemplate object.  The unique name of the object in the API. This name can contain only underscores and alphanumeric characters, and must be unique in your org. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. In managed packages, this field prevents naming conflicts on package installations. With this field, a developer can change the object’s name in a managed package and the changes are reflected in a subscriber’s organization. Label is **Record Type Name**. This field is automatically generated, but you can supply your own value if you create the record using the API. |
| EmtUsageType | Type  Picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  A explainability message template’s usage type. This field is available from API version 60.0 and later.  Possible values are:  - `Bre`–Default - `ProductCategoryQualification` - `ProductQualification` - `RecordAlert`  Note Note When Business Rules Engine is enabled for a Salesforce instance, the default value is '`Bre`’. Other usage types may be available to you depending on your industry solution and permission sets. |
| ExpressionSetStepType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The step type in an expression set that uses the explainability message template. This is a required field.  Possible values are:  - `Aggregation` - `Branch` - `BusinessElement` - `Calculation` - `Condition` - `DecisionTableLookup` - `ListFilter`—This   value is available from API version 59.0 and later. - `ListEnabledGroup`—This value is available   from API version 59.0 and later. - `MatrixLookup` - `PredictiveAI` - `ReferenceProcedure`  The default value is `Calculation`. |
| IsDefault | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the explainability message template for a specified step type is default (`true`) or not (`false`).  The default value is `false`. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The language in which the message in the explainability message template is created.  Possible values are:  - `da`—Danish - `de`—German - `en_US`—English - `es`—Spanish - `es_MX`—Spanish   (Mexico) - `fi`—Finnish - `fr`—French - `it`—Italian - `ja`—Japanese - `ko`—Korean - `nl_NL`—Dutch - `no`—Norwegian - `pt_BR`—Portuguese   (Brazil) - `ru`—Russian - `sv`—Swedish - `th`—Thai - `zh_CN`—Chinese   (Simplified) - `zh_TW`—Chinese   (Traditional) |
| ManageableState | Type  ManageableState enumerated list  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package:  - `beta` - `deleted` - `deprecated` - `deprecatedEditable` - `installed` - `installedEditable` - `released` - `unmanaged` |
| MasterLabel | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The label for ExplainabilityMsgTemplate. In the UI, this field id Explainability Message Template. |
| Message | Type  textarea  Properties  Create, Filter, Sort, Update  Description  The message associated with the template for a specific expression set step type. This is a required field. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix associated with this object. Each Developer Edition organization that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `namespacePrefix__componentName` notation. The namespace prefix can have one of the following values:   - In Developer Edition organizations, the namespace prefix is   set to the namespace prefix of the organization for all   objects that support it. There is an exception if an object   is in an installed managed package. In that case, the object   has the namespace prefix of the installed managed package.   This field’s value is the namespace prefix of the Developer   Edition organization of the package developer. - In organizations that are not Developer Edition   organizations, NamespacePrefix is only   set for objects that are part of an installed managed   package. There is no namespace prefix for all other   objects. |
| ResultType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of result for which the message template can be used. The step type for which the result is evaluated can be a condition, conditional group, or branch. This is a required field.  Possible values are:  - `Failed` - `NoResult`—This   value is available from API version 59.0 and later. - `Passed`  The default value is `Passed`. |
