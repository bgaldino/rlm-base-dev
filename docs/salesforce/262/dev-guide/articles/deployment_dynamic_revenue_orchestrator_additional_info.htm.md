---
page_id: deployment_dynamic_revenue_orchestrator_additional_info.htm
title: Dynamic Revenue Orchestrator Additional Information
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_dynamic_revenue_orchestrator_additional_info.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_C.htm
fetched_at: 2026-06-09
---

# Dynamic Revenue Orchestrator Additional Information

Get to know additional deployment information for Dynamic Revenue Orchestrator (DRO) in
Revenue Cloud, including active or inactive states, object information, and migration
considerations.

## Object-Specific Information

| Object Name | Object API | Notes |
| --- | --- | --- |
| Product Fulfillment Decomposition Rule | ProductFulfillmentDecompRule | Rule set references are created in the target org by using UPDATE operation on the JSON fields as listed in the Special Fields section. Any rule set records and references aren’t created on INSERT operation. |
| Fulfillment Step Definition | FulfillmentStepDefinition | Rule set references are created in the target org by using UPDATE operation on the JSON fields as listed in the Special Fields section. Any rule set records and references aren’t created on INSERT operation. |
| Product Fulfillment Scenario | ProductFulfillmentScenario | Rule set references are created in the target org by using UPDATE operation on the JSON fields as listed in the Special Fields section. Any rule set records and references aren’t created on INSERT operation. |
| Fulfillment Fallout Rule | FulfillmentFalloutRule | After migration, refresh the related Decision Tables. |
| Fulfillment Task Assignment Rule | FulfillmentTaskAssignmentRule | Rule set references are created in the target org by using UPDATE operation on the JSON fields as listed in the Special Fields section. Any rule set records and references aren’t created on INSERT operation. |
| Orchestration Plan Context Mapping | OrchestrationPlanCtxMapping | This setup object is always active after creation. Here are some considerations.  - The object must have an active context definition to create the mapping. - The context definition must remain active for the mapping to be valid. - Context nodes or referenced mappings must exist in the active context   definition version. |

## Special Fields

- These objects use a large text field to contain a JSON representation of Dynamic Revenue
  Orchestrator (DRO) condition data, backed up by internal Business Rules Engine (BRE)
  RuleSet objects.
  - FulfillmentStepDefinition
    - ExecuteOnConditionData. This is related to ExecuteOnRule field (RuleSet
      reference).
    - ResumeOnConditionData. This is related to ResumeOnRule field (RuleSet
      reference).
  - ProductFulfillmentScenario
    - ConditionData. This is related to ScenarioRule field (RuleSet reference).
  - ProductFulfillmentDecompRule
    - ConditionData. This is related to ExecuteOnRule field (RuleSet reference).
  - FulfillmentTaskAssignmentRule
    - ConditionData. This is related to Condition field (RuleSet reference).

## Other Information

- Migration Prerequisites
  - When DRO is enabled in a new org, the system provides an built-in library named as
    DRORuleLibrary. See [Dynamic Fulfillment
    Orchestrator Settings](https://developer.salesforce.com/docs/./meta_dynamicfulfillmentorchestratorsettings.htm.md "HTML (New Window)").
  - Context rules library is Active with `Usage
    Type=Dfo` and is linked with Sales Context Definition.
  - The active rule library version must point to the context definition currently
    configured in the DRO Admin settings. If you change the context definition in the
    settings, you must create a new rule library version that links to the new
    definition and activate it.

    When creating a version, you must clone from the latest rule library version. If
    you clone from an older version instead of the latest, any rule sets created in the
    latest version is lost in any other newly created version. This leads to evaluation
    errors where rules evaluate to `false` as the
    engine is unable to find the rule set in the active library.

    When moving to a new version, you must first deactivate the older version and then
    activate the cloned version.
  - Context definitions must have the necessary nodes, mappings, and context tags used
    in rule sets.
  - DRO rules include Product Fulfillment Decomposition Rule, Fulfillment Step
    Definition, Product Fulfillment Scenario, and Fulfillment Task Assignment Rule
    objects. To migrate DRO rules or scenarios, make sure the AttributeDefinition and
    AttributePicklistValue records are referenced in condition data fields by attribute
    code and picklist value name in the org before migration. The code value is defined in
    product management records.
  - The SourceAttributeIdentifier and DestinationAttributeIdentifier fields of a
    ProductDecompEnrichmentRule record can include attribute IDs from the source org,
    leading to invalid references in the target org. Refresh the identifier fields by
    saving the ProductDecompEnrichmentRule records again. You can also set the identifier
    fields to null during migration to make sure that they auto-populate correctly.
  - Before you can migrate the Product Fulfillment Decomposition Rule, Fulfillment Step Definition,
    Product Fulfillment Scenario, and Fulfillment Task Assignment Rule objects with
    their related child records, several other key records must exist in the target
    Salesforce org. Migrating these records first is crucial to maintain data integrity
    and to make sure that the relationships are correctly established in rules.

    Here are the required records in the target org as per the required migration sequence.

    - Products (Product2)—The top-level ProductFulfillmentDecompRule record is directly linked
      to a specific product via the ProductId field. You can’t create the rule without
      associating it with an existing product record.

      Make sure that the Product2 records in the source and target orgs can be
      uniquely identified. For example, use a custom external ID field such as
      GlobalKey\_\_c or any other ExternalId field, or use the standard ProductCode
      field.
    - Attribute Definitions (AttributeDefinition)—The ProductDecompEnrichmentRule records, which
      are children of the decomposition rule, use attribute definitions to specify
      which product attributes to use for enrichment or transformation. These rules
      reference AttributeDefinition records in fields, such as
      SourceAttributeDefinitionId and TargetAttributeDefinitionId. DRO Condition Data
      fields and rule sets use AttributeCode values in Condition Expressions.

      Attribute Definitions must be migrated before the enrichment rules to make sure
      that the lookup relationships are resolved successfully. Attribute Code values
      must be defined as these values are used in DRO Conditions as unique identifiers
      for attribute-type expressions.
    - Attribute Definition Picklist Values (AttributePicklistValue)—The ValTfrm (Value
      Transform) records, which are used for mapping and transforming data, often rely
      on picklist values defined in the AttributePicklistValue object. These records
      define the specific values used in the transformation logic. DRO Condition Data
      fields and rule sets use AttributeCode values in Condition Expressions.

      If your transformation rules involve picklist
      fields, you must migrate the corresponding AttributePicklistValue records
      first.
- DRO Rules and Scenario Migration
  - Internal rule set tables may contain attribute ID values, which are the Salesforce
    IDs of the relevant AttributeDefinition records of the Product or Product
    Classification.
  - DRO stores rule set-related data in string representation with AttributeDefinition.
    During migration, the JSON representation of a rule set uses Attribute Code as the
    natural key to resolve AttributeDefinition records and set as key in internal rule set
    tables. As a prerequisite, make sure that attribute code values are populated and
    consistent in both the source and target orgs before you migrate DRO rules.
  - Rule sets also contain attribute picklist values in condition expressions. The
    AttributePicklistValue records of the associated AttributeDefinition records must
    exist in target org before you migrate DRO rules.
  - You can’t insert a new DRO rule record with condition data. You can only update the
    record. In such a scenario, migrate the rule record with an empty condition field
    through an INSERT operation. Then, perform an UPDATE operation on the condition field
    with the JSON value from the source org.
- After Migration:
  - Refresh the Decision Tables (DT) used by DRO Fallout Management—Migrating the
    Fulfillment Fallout Rules records requires a refreshed Fallout Rules DT
    definition.
  - Refresh DTs used by DRO Jeopardy Management—Migrating the Fulfillment Step
    Jeopardy Rule records requires a refreshed Fulfillment Step Jeopardy Rule DT
    definition.
  - Make sure to activate technical products in your target org as part of your
    deployment.
- These components have dependencies on Industries common features:
  - Enrichment Rule—Expression Set
  - Decomposition Rule with condition—Business Rules Engine Context Rule and
    Context Service
  - Callout step—Integration Definition
  - Autotask step—Flow
  - Manual Task step—Queue
  - Product Fulfillment Scenario with condition—Business Rules Engine Context
    Rule and Context Service

#### See Also

- [*Bulk API 2.0 and Bulk API Developer Guide*: Introduction to Bulk API 2.0 and
  Bulk API](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_asynch.meta/api_asynch/asynch_api_intro.htm "Bulk API 2.0 and Bulk API Developer Guide: Introduction to Bulk API 2.0 and
         Bulk API - HTML (New Window)")
