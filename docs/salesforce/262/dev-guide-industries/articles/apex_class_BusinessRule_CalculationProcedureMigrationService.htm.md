---
page_id: apex_class_BusinessRule_CalculationProcedureMigrationService.htm
title: CalculationProcedureMigrationService Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/apex_class_BusinessRule_CalculationProcedureMigrationService.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: apex_namespace_BusinessRule.htm
fetched_at: 2026-06-25
---

# CalculationProcedureMigrationService Class

Contains methods for migrating calculation procedures from the Vlocity
package to the Business Rules Engine as expression sets.

## Namespace

[BusinessRule](./apex_namespace_BusinessRule.htm.md "The BusinessRule namespace provides classes for migrating calculation matrices and calculation procedures from Vlocity to the Business Rules Engine in Salesforce.")

## Usage

Consider these guidelines before migrating a calculation procedure that uses a calculation matrix.

- Migrate the calculation matrix first. This creates a decision matrix.
- Add data to the decision matrix and activate it.

## Example

This example converts a list of calculation procedure IDs to expression set IDs and logs
the result in the debug log.

```
List<String> calcProcIds = new List<String>();
calcProcIds.add('a00xx000000boy5AAA');
calcProcIds.add('a00xx000000bozhAAA');
calcProcIds.add('a00xx000000bp1JAAQ');

System.debug('TO MIGRATE A LIST OF CALCULATION PROCEDURES');
System.debug(BusinessRule.CalculationProcedureMigrationService.migrate(calcProcIds, 'vlocity_ins'));
```

This example converts a calculation procedure ID to an expression set ID and logs the
result in the debug log.

```
System.debug('TO MIGRATE A CALCULATION PROCEDURE');
System.debug(BusinessRule.CalculationProcedureMigrationService.migrate('a00xx000000bp2vAAA', 'vlocity_ins'));
```

- **[CalculationProcedureMigrationService Methods](./apex_class_BusinessRule_CalculationProcedureMigrationService.htm.md#apex_BusinessRule_CalculationProcedureMigrationService_methods)**

## CalculationProcedureMigrationService Methods

The following are methods for `CalculationProcedureMigrationService`.

- **[migrate(calcProcedureIds, namespace)](./apex_class_BusinessRule_CalculationProcedureMigrationService.htm.md#apex_BusinessRule_CalculationProcedureMigrationService_migrate)**  
  Migrate calculation procedures from the Vlocity package as expression sets to the Business Rules Engine.
- **[migrate(calcProcedureId, namespace)](./apex_class_BusinessRule_CalculationProcedureMigrationService.htm.md#apex_BusinessRule_CalculationProcedureMigrationService_migrate_2)**  
  Migrate a calculation procedure from the Vlocity package as an expression set to the Business Rules Engine.

### migrate(calcProcedureIds, namespace)

Migrate calculation procedures from the Vlocity package as expression
sets to the Business Rules Engine.

#### Signature

`public static Map<String,Object> migrate(List<String>
calcProcedureIds, String namespace)`

#### Parameters

calcProcedureIds
:   Type: List<String>
:   The 18-character IDs of the calculation procedures in the Vlocity managed package to be migrated
    to the Business Rules Engine as expression sets.

    18 character ID.

namespace
:   Type: String
:   The namespace in which Vlocity is deployed as a
    managed package. For example, `vlocity_ins`. This contains the calculation procedure
    custom objects.

#### Return Value

Type: Map<String,Object>

### migrate(calcProcedureId, namespace)

Migrate a calculation procedure from the Vlocity package as an
expression set to the Business Rules Engine.

#### Signature

`public static Map<String,Object> migrate(String
calcProcedureId, String namespace)`

#### Parameters

calcProcedureId
:   Type: String
:   The 18-character ID of the calculation procedure in the Vlocity managed package to be migrated
    to the Business Rules Engine as an expression set.

namespace
:   Type: String
:   The namespace in which Vlocity is deployed as a managed package. For example, `vlocity_ins`. This contains the calculation procedure
    custom objects.

#### Return Value

Type: Map<String,Object>
