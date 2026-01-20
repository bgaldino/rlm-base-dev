# QB-DRO Scratch Data File Validation

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
