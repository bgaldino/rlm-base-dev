# QB-PRICING Data File Validation

Validates CSV data files for externalId completeness and duplicate keys.

## CurrencyType

- Operation: Insert
- ExternalId: IsoCode
- CSV: CurrencyType.csv

- Rows: 7
- Blank key rows: 0
- Duplicate keys: 0

## ProrationPolicy

- Operation: Upsert
- ExternalId: Name
- CSV: ProrationPolicy.csv

- Rows: 1
- Blank key rows: 0
- Duplicate keys: 0

## ProductSellingModel

- Operation: Readonly
- ExternalId: Name;SellingModelType
- CSV: ProductSellingModel.csv

- Rows: 9
- Blank key rows: 0
- Duplicate keys: 0

## AttributeDefinition

- Operation: Readonly
- ExternalId: Code
- CSV: AttributeDefinition.csv

- Rows: 39
- Blank key rows: 0
- Duplicate keys: 0

## Product2

- Operation: Readonly
- ExternalId: StockKeepingUnit
- CSV: Product2.csv

- Rows: 152
- Blank key rows: 0
- Duplicate keys: 0

## Pricebook2

- Operation: Upsert
- ExternalId: Name;IsStandard
- CSV: Pricebook2.csv

- Rows: 1
- Blank key rows: 0
- Duplicate keys: 0

## CostBook

- Operation: Upsert
- ExternalId: Name;IsDefault
- CSV: CostBook.csv

CSV empty.

## PriceAdjustmentTier

- Operation: Upsert
- ExternalId: PriceAdjustmentSchedule.Name;Product2.StockKeepingUnit;ProductSellingModel.Name;ProductSellingModel.SellingModelType;TierType;TierValue;LowerBound;CurrencyIsoCode;EffectiveFrom
- CSV: PriceAdjustmentTier.csv

- Rows: 3
- Blank key rows: 0
- Duplicate keys: 0

## PriceAdjustmentSchedule

- Operation: Update
- ExternalId: Name;CurrencyIsoCode;Pricebook2.Name
- CSV: PriceAdjustmentSchedule.csv

- Rows: 4
- Blank key rows: 0
- Duplicate keys: 0

## AttributeBasedAdjRule

- Operation: Upsert
- ExternalId: Name
- CSV: AttributeBasedAdjRule.csv

- Rows: 4
- Blank key rows: 0
- Duplicate keys: 0

## AttributeAdjustmentCondition

- Operation: Upsert
- ExternalId: AttributeBasedAdjRule.Name;AttributeDefinition.Code;Product.StockKeepingUnit
- CSV: AttributeAdjustmentCondition.csv

- Rows: 4
- Blank key rows: 0
- Duplicate keys: 0

## AttributeBasedAdjustment

- Operation: Upsert
- ExternalId: AttributeBasedAdjRule.Name;PriceAdjustmentSchedule.Name;Product.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode
- CSV: AttributeBasedAdjustment.csv

- Rows: 4
- Blank key rows: 0
- Duplicate keys: 0

## BundleBasedAdjustment

- Operation: Upsert
- ExternalId: PriceAdjustmentSchedule.Name;Product.StockKeepingUnit;ParentProduct.StockKeepingUnit;RootBundle.StockKeepingUnit;ProductSellingModel.Name;ParentProductSellingModel.Name;RootProductSellingModel.Name;CurrencyIsoCode
- CSV: BundleBasedAdjustment.csv

- Rows: 2
- Blank key rows: 0
- Duplicate keys: 0

## PricebookEntry

- Operation: Upsert
- ExternalId: Name;Pricebook2.Name;Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode
- CSV: PricebookEntry.csv

- Rows: 114
- Blank key rows: 0
- Duplicate keys: 0

## PricebookEntryDerivedPrice

- Operation: Upsert
- ExternalId: Pricebook.Name;PricebookEntry.Name;Product.StockKeepingUnit;ContributingProduct.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode
- CSV: PricebookEntryDerivedPrice.csv

- Rows: 2
- Blank key rows: 0
- Duplicate keys: 0

## CostBookEntry

- Operation: Upsert
- ExternalId: CostBook.Name;Product.StockKeepingUnit;CurrencyIsoCode
- CSV: CostBookEntry.csv

CSV empty.
