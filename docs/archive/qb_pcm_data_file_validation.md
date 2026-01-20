# QB-PCM Data File Validation

Validates CSV data files for externalId completeness and duplicate keys.

## AttributePicklist

- Operation: Upsert
- ExternalId: Name
- CSV: AttributePicklist.csv

- Rows: 25
- Blank key rows: 0
- Duplicate keys: 0

## AttributePicklistValue

- Operation: Upsert
- ExternalId: Code
- CSV: AttributePicklistValue.csv

- Rows: 87
- Blank key rows: 0
- Duplicate keys: 0

## UnitOfMeasureClass

- Operation: Upsert
- ExternalId: Code
- CSV: UnitOfMeasureClass.csv

- Rows: 5
- Blank key rows: 0
- Duplicate keys: 0

## UnitOfMeasure

- Operation: Upsert
- ExternalId: UnitCode
- CSV: UnitOfMeasure.csv

- Rows: 12
- Blank key rows: 0
- Duplicate keys: 0

## AttributeDefinition

- Operation: Upsert
- ExternalId: Code
- CSV: AttributeDefinition.csv

- Rows: 39
- Blank key rows: 0
- Duplicate keys: 0

## AttributeCategory

- Operation: Upsert
- ExternalId: Code
- CSV: AttributeCategory.csv

- Rows: 18
- Blank key rows: 0
- Duplicate keys: 0

## AttributeCategoryAttribute

- Operation: Upsert
- ExternalId: AttributeCategory.Code;AttributeDefinition.Code
- CSV: AttributeCategoryAttribute.csv

- Rows: 34
- Blank key rows: 0
- Duplicate keys: 0

## ProductClassification

- Operation: Upsert
- ExternalId: Code
- CSV: ProductClassification.csv

- Rows: 16
- Blank key rows: 0
- Duplicate keys: 0

## ProductClassificationAttr

- Operation: Upsert
- ExternalId: ProductClassification.Code;AttributeDefinition.Code;AttributeCategory.Code
- CSV: ProductClassificationAttr.csv

- Rows: 36
- Blank key rows: 4
- Duplicate keys: 0

## Product2

- Operation: Upsert
- ExternalId: StockKeepingUnit
- CSV: Product2.csv

- Rows: 164
- Blank key rows: 0
- Duplicate keys: 0

## ProductAttributeDefinition

- Operation: Upsert
- ExternalId: AttributeDefinition.Code;Product2.StockKeepingUnit
- CSV: ProductAttributeDefinition.csv

- Rows: 17
- Blank key rows: 0
- Duplicate keys: 0

## ProductSellingModel

- Operation: Upsert
- ExternalId: Name;SellingModelType
- CSV: ProductSellingModel.csv

- Rows: 9
- Blank key rows: 0
- Duplicate keys: 0

## ProrationPolicy

- Operation: Upsert
- ExternalId: Name
- CSV: ProrationPolicy.csv

- Rows: 1
- Blank key rows: 0
- Duplicate keys: 0

## ProductSellingModelOption

- Operation: Upsert
- ExternalId: Product2.StockKeepingUnit;ProductSellingModel.Name;ProductSellingModel.SellingModelType
- CSV: ProductSellingModelOption.csv

- Rows: 115
- Blank key rows: 0
- Duplicate keys: 0

## ProductRampSegment

- Operation: Upsert
- ExternalId: Product.StockKeepingUnit;ProductSellingModel.SellingModelType;SegmentType
- CSV: ProductRampSegment.csv

- Rows: 5
- Blank key rows: 0
- Duplicate keys: 0

## ProductRelationshipType

- Operation: Upsert
- ExternalId: Name
- CSV: ProductRelationshipType.csv

- Rows: 4
- Blank key rows: 0
- Duplicate keys: 0

## ProductComponentGroup

- Operation: Upsert
- ExternalId: Code;ParentProduct.StockKeepingUnit
- CSV: ProductComponentGroup.csv

- Rows: 26
- Blank key rows: 0
- Duplicate keys: 0

## ProductRelatedComponent

- Operation: Upsert
- ExternalId: ChildProductClassification.Code;ChildProduct.StockKeepingUnit;ParentProduct.StockKeepingUnit;ProductComponentGroup.Code;ProductRelationshipType.Name
- CSV: ProductRelatedComponent.csv

- Rows: 78
- Blank key rows: 78
- Duplicate keys: 0

## ProductComponentGrpOverride

- Operation: Upsert
- ExternalId: Name
- CSV: ProductComponentGrpOverride.csv

CSV empty.

## ProductRelComponentOverride

- Operation: Upsert
- ExternalId: ProductRelatedComponent.Name;OverrideContext.StockKeepingUnit
- CSV: ProductRelComponentOverride.csv

CSV empty.

## ProductCatalog

- Operation: Upsert
- ExternalId: Code
- CSV: ProductCatalog.csv

- Rows: 3
- Blank key rows: 0
- Duplicate keys: 0

## ProductCategory

- Operation: Upsert
- ExternalId: Code
- CSV: ProductCategory.csv

- Rows: 18
- Blank key rows: 0
- Duplicate keys: 0

## ProductCategoryProduct

- Operation: Upsert
- ExternalId: ProductCategory.Code;Product.StockKeepingUnit
- CSV: ProductCategoryProduct.csv

- Rows: 98
- Blank key rows: 0
- Duplicate keys: 0

## ProductQualification

- Operation: 
- ExternalId: Name
- CSV: ProductQualification.csv

CSV empty.

## ProductDisqualification

- Operation: 
- ExternalId: Name
- CSV: ProductDisqualification.csv

CSV empty.

## ProductCategoryDisqual

- Operation: 
- ExternalId: Name
- CSV: ProductCategoryDisqual.csv

CSV empty.

## ProductCategoryQualification

- Operation: 
- ExternalId: Name
- CSV: ProductCategoryQualification.csv

CSV empty.

## ProdtAttrScope

- Operation: 
- ExternalId: Name
- CSV: ProdtAttrScope.csv

- Rows: 3
- Blank key rows: 0
- Duplicate keys: 0
