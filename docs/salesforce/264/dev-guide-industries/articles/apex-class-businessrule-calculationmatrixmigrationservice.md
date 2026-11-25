---
page_id: apex-class-businessrule-calculationmatrixmigrationservice
title: CalculationMatrixMigrationService Class
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/apex-class-businessrule-calculationmatrixmigrationservice.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: apex-namespace-businessrule
legacy_page_id: apex_class_BusinessRule_CalculationMatrixMigrationService.htm
fetched_at: 2026-11-25
---

# CalculationMatrixMigrationService Class

Contains methods for migrating calculation matrices from the Vlocity package to the Business Rules Engine as decision matrices.

## Namespace

[BusinessRule](./apex-namespace-businessrule.md)

## Example

This example converts a list of calculation matrix IDs to decision matrix IDs and logs the result in the debug log.

```
List<String> ids = new List<String>();
ids.add('a03xx000004WhvkAAC');
ids.add('a03xx000004WhxMAAS');
ids.add('a03xx000004WhyyAAC');

System.debug('TO MIGRATE A LIST OF CALCULATION MATRICES');
System.debug(BusinessRule.CalculationMatrixMigrationService.migrate(ids, 'vlocity_ins'));
```

This example converts a calculation matrix ID to a decision matrix ID and logs the result in the debug log.

```
System.debug('TO MIGRATE A CALCULATION MATRIX');
System.debug(BusinessRule.CalculationMatrixMigrationService.migrate('a03xx000004Wi0aAAC', 'vlocity_ins'));
```

- **[CalculationMatrixMigrationService Methods](#calculationmatrixmigrationservice-methods)**

## CalculationMatrixMigrationService Methods

The following are methods for `CalculationMatrixMigrationService`.

- 

**[migrate(calculationMatrixIds, namespace)](#migratecalculationmatrixids-namespace)**

Migrate calculation matrices from the Vlocity package to the Business Rules Engine as decision matrices.

- 

**[migrate(calculationMatrixId, namespace)](#migratecalculationmatrixid-namespace)**

Migrate a calculation matrix from the Vlocity package as a decision matrix to the Business Rules Engine.

### migrate(calculationMatrixIds, namespace)

Migrate calculation matrices from the Vlocity package to the Business Rules Engine as decision matrices.

#### Signature

`public static Map<String,Object> migrate(List<String> calculationMatrixIds, String namespace)`

#### Parameters

***calculationMatrixIds***

: 

Type: List<[String](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_methods_system_string.htm#apex_methods_system_string)>

The 18-character IDs of the calculation matrices in the Vlocity managed package to be migrated to the Business Rules Engine as decision matrices.

***namespace***

: 

Type: [String](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_methods_system_string.htm#apex_methods_system_string)

The namespace in which Vlocity is deployed as a managed package. For example, `vlocity_ins`. This contains the calculation matrix custom objects.

#### Return Value

Type: Map<[String](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_methods_system_string.htm#apex_methods_system_string),Object>

### migrate(calculationMatrixId, namespace)

Migrate a calculation matrix from the Vlocity package as a decision matrix to the Business Rules Engine.

#### Signature

`public static Map<String,Object> migrate(String calculationMatrixId, String namespace)`

#### Parameters

***calculationMatrixId***

: 

Type: String

The 18-character ID of the calculation matrix in the Vlocity managed package to be migrated to the Business Rules Engine as a decision matrix.

***namespace***

: 

Type: String

The namespace in which Vlocity is deployed as a managed package. For example, `vlocity_ins`. This contains the calculation matrix custom objects.

#### Return Value

Type: Map<String,Object>

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/apex-class-businessrule-calculationmatrixmigrationservice.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
