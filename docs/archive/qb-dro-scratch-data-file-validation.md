# QB-DRO Scratch Data File Validation (Retired)

**Deprecated:** The `qb-dro_scratch` data plan has been removed. DRO data is now loaded from the single **qb-dro** plan with dynamic AssignedTo user resolution: the task `insert_qb_dro_data_scratch` / `insert_qb_dro_data_prod` uses the option `dynamic_assigned_to_user: true` and replaces the placeholder `__DRO_ASSIGNED_TO_USER__` in `FulfillmentStepDefinition.csv` and `UserAndGroup.csv` with the target org’s default user Name (e.g. "User User" in scratch orgs, "Admin User" in TSO). See `tasks/rlm_sfdmu.py` and `cumulusci.yml` (prepare_dro flow, quantumbit_dro_dataset).

---

*Original content: validation of the former qb-dro_scratch CSV files.*

Validates CSV data files for externalId completeness and duplicate keys.

## FulfillmentWorkspace

- Operation: Upsert
- ExternalId: Name;CurrencyIsoCode
- CSV: FulfillmentWorkspace.csv

- Rows: 1
- Blank key rows: 0
- Duplicate keys: 0

## FulfillmentStepDefinitionGroup

- Operation: Upsert
- ExternalId: Name;CurrencyIsoCode
- CSV: FulfillmentStepDefinitionGroup.csv

- Rows: 4
- Blank key rows: 0
- Duplicate keys: 0

## FulfillmentFalloutRule

- Operation: Upsert
- ExternalId: Name;CurrencyIsoCode
- CSV: FulfillmentFalloutRule.csv

- Rows: 1
- Blank key rows: 0
- Duplicate keys: 0

## FulfillmentStepJeopardyRule

- Operation: Upsert
- ExternalId: Name;CurrencyIsoCode
- CSV: FulfillmentStepJeopardyRule.csv

- Rows: 3
- Blank key rows: 0
- Duplicate keys: 0

## FulfillmentStepDefinition

- Operation: Upsert
- ExternalId: Name;StepDefinitionGroup.Name;CurrencyIsoCode
- CSV: FulfillmentStepDefinition.csv

- Rows: 6
- Blank key rows: 0
- Duplicate keys: 0

## FulfillmentStepDependencyDef

- Operation: Upsert
- ExternalId: Name;DependsOnStepDefinition.Name;FulfillmentStepDefinition.Name;CurrencyIsoCode
- CSV: FulfillmentStepDependencyDef.csv

- Rows: 5
- Blank key rows: 0
- Duplicate keys: 0

## FulfillmentWorkspaceItem

- Operation: Upsert
- ExternalId: FulfillmentWorkspace.Name;FulfillmentStepDefinitionGroup.Name;CurrencyIsoCode
- CSV: FulfillmentWorkspaceItem.csv

- Rows: 3
- Blank key rows: 0
- Duplicate keys: 0

## ProductFulfillmentDecompRule

- Operation: Upsert
- ExternalId: Name;SourceProduct.StockKeepingUnit;DestinationProduct.StockKeepingUnit;CurrencyIsoCode
- CSV: ProductFulfillmentDecompRule.csv

- Rows: 30
- Blank key rows: 0
- Duplicate keys: 0

## ProductFulfillmentScenario

- Operation: Upsert
- ExternalId: Name;Product.StockKeepingUnit;CurrencyIsoCode
- CSV: ProductFulfillmentScenario.csv

- Rows: 10
- Blank key rows: 0
- Duplicate keys: 0

## Product2

- Operation: Update
- ExternalId: Name;StockKeepingUnit
- CSV: Product2.csv

- Rows: 98
- Blank key rows: 0
- Duplicate keys: 0
