# QB-TAX Data File Validation

Validates CSV data files for externalId completeness and duplicate keys.

## LegalEntity

- Operation: Upsert
- ExternalId: Name
- CSV: LegalEntity.csv

- Rows: 2
- Blank key rows: 0
- Duplicate keys: 0

## TaxEngineProvider

- Operation: Upsert
- ExternalId: DeveloperName
- CSV: TaxEngineProvider.csv

- Rows: 1
- Blank key rows: 0
- Duplicate keys: 0

## TaxEngine

- Operation: Upsert
- ExternalId: TaxEngineName
- CSV: TaxEngine.csv

- Rows: 1
- Blank key rows: 0
- Duplicate keys: 0

## TaxTreatment

- Operation: Upsert
- ExternalId: Name;LegalEntity.Name;TaxPolicy.Name
- CSV: TaxTreatment.csv

- Rows: 1
- Blank key rows: 0
- Duplicate keys: 0

## TaxPolicy

- Operation: Upsert
- ExternalId: Name
- CSV: TaxPolicy.csv

- Rows: 1
- Blank key rows: 0
- Duplicate keys: 0

## Product2

- Operation: Update
- ExternalId: StockKeepingUnit
- CSV: Product2.csv

- Rows: 105
- Blank key rows: 0
- Duplicate keys: 0
