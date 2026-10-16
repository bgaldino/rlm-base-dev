---
page_id: apex_class_BusinessRule_CalculationMatrixMigrationService.htm
title: CalculationMatrixMigrationService Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/apex_class_BusinessRule_CalculationMatrixMigrationService.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: apex_namespace_BusinessRule.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# CalculationMatrixMigrationService Class

Contains methods for migrating calculation matrices from the Vlocity
      package to the Business Rules Engine as decision matrices.

## Namespace

[BusinessRule](./apex_namespace_BusinessRule.htm.md)

## Example

      This example converts a list of calculation matrix IDs to decision matrix IDs and logs the
        result in the debug log.

```

List<String> ids = new List<String>();
ids.add('a03xx000004WhvkAAC');
ids.add('a03xx000004WhxMAAS');
ids.add('a03xx000004WhyyAAC');

System.debug('TO MIGRATE A LIST OF CALCULATION MATRICES');
System.debug(BusinessRule.CalculationMatrixMigrationService.migrate(ids, 'vlocity_ins'));

```

      This example converts a calculation matrix ID to a decision matrix ID and logs the result
        in the debug log.

```

System.debug('TO MIGRATE A CALCULATION MATRIX');
System.debug(BusinessRule.CalculationMatrixMigrationService.migrate('a03xx000004Wi0aAAC', 'vlocity_ins'));

```

- 
**[CalculationMatrixMigrationService Methods](./apex_class_BusinessRule_CalculationMatrixMigrationService.htm.md#apex_BusinessRule_CalculationMatrixMigrationService_methods)**  

## CalculationMatrixMigrationService Methods

The following are methods for `CalculationMatrixMigrationService`.

- 
**[migrate(calculationMatrixIds, namespace)](./apex_class_BusinessRule_CalculationMatrixMigrationService.htm.md#apex_BusinessRule_CalculationMatrixMigrationService_migrate)**  

Migrate calculation matrices from the Vlocity package to the Business       Rules Engine as decision matrices.

- 
**[migrate(calculationMatrixId, namespace)](./apex_class_BusinessRule_CalculationMatrixMigrationService.htm.md#apex_BusinessRule_CalculationMatrixMigrationService_migrate_2)**  

Migrate a calculation matrix from the Vlocity package as a decision       matrix to the Business Rules Engine.

### migrate(calculationMatrixIds, namespace)

Migrate calculation matrices from the Vlocity package to the Business
      Rules Engine as decision matrices.

#### Signature

`public static Map<String,Object> migrate(List<String> calculationMatrixIds, String namespace)`

#### Parameters

**calculationMatrixIds**

: Type: List<String>

: The 18-character IDs of the calculation matrices in the Vlocity managed package to be migrated
            to the Business Rules Engine as decision matrices.

**namespace**

: Type: String

: The namespace in which Vlocity is deployed as a managed package. For example,
                `vlocity_ins`. This contains the calculation
              matrix custom objects.

#### Return Value

Type: Map<String,Object>

### migrate(calculationMatrixId, namespace)

Migrate a calculation matrix from the Vlocity package as a decision
      matrix to the Business Rules Engine.

#### Signature

`public static Map<String,Object> migrate(String calculationMatrixId, String namespace)`

#### Parameters

**calculationMatrixId**

: Type: String

: The 18-character ID of the calculation matrix in the Vlocity managed package to be migrated to
            the Business Rules Engine as a decision matrix.

**namespace**

: Type: String

          
: The namespace in which Vlocity is deployed as a managed package. For example, `vlocity_ins`. This contains the calculation matrix
            custom objects.

#### Return Value

Type: Map<String,Object>
