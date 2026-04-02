# PCM — Product Catalog Management

11 core objects managing the product catalog: products, attributes, classifications, bundles, categories, and qualifications.

## Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `Product2` | Central product record | StockKeepingUnit (unique), Name, ProductCode, Family, IsActive, BillingPolicyId, TaxPolicyId, UsageModelType |
| `AttributePicklist` | Picklist definitions for product attributes | Name, UnitOfMeasureId |
| `AttributePicklistValue` | Individual values within an attribute picklist | Code, AttributePicklistId |
| `AttributeDefinition` | Defines a product attribute (size, color, etc.) | Code, PicklistId, UnitOfMeasureId, DataType |
| `AttributeCategory` | Groups attributes into categories | Code, Name |
| `AttributeCategoryAttribute` | Junction: category ↔ attribute | AttributeCategoryId, AttributeDefinitionId |
| `ProductAttributeDefinition` | Binds an attribute to a specific product | Product2Id, AttributeDefinitionId, AttributeCategoryId |
| `ProductClassification` | Hierarchical product taxonomy | Code, ParentProductClassificationId (self-ref) |
| `ProductClassificationAttr` | Attribute assigned at classification level | ProductClassificationId, AttributeDefinitionId |
| `ProductCategory` | Catalog categories (hierarchical) | Code, CatalogId, ParentCategoryId (self-ref) |
| `ProductCategoryProduct` | Junction: category ↔ product | ProductCategoryId, ProductId, CatalogId |

## Bundle/Component Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `ProductRelationshipType` | Defines relationship types (Bundle, Add-On, etc.) | Name |
| `ProductComponentGroup` | Groups of components within a bundle | Code, ParentProductId, ParentGroupId (self-ref) |
| `ProductRelatedComponent` | Specific component within a group | ChildProductId, ParentProductId, ProductComponentGroupId, ProductRelationshipTypeId |
| `ProductSellingModel` | How a product is sold (One-Time, Evergreen, Term) | Name, SellingModelType |
| `ProductSellingModelOption` | Binds a selling model to a product | Product2Id, ProductSellingModelId, ProrationPolicyId |
| `ProrationPolicy` | Proration rules for partial periods | Name |
| `ProductRampSegment` | Ramp schedule segments for a product | ProductId, ProductSellingModelId, SegmentType |
| `ProductCatalog` | Top-level catalog container | Code |

## Qualification/Disqualification Objects

| Object | Purpose |
|--------|---------|
| `ProductQualification` | Rules qualifying a product within a bundle context |
| `ProductDisqualification` | Rules disqualifying a product |
| `ProductCategoryQualification` | Category-level qualification rules |
| `ProductCategoryDisqual` | Category-level disqualification rules |

## Key Relationships

```
AttributePicklist ← AttributePicklistValue (PicklistId)
AttributePicklist ← AttributeDefinition (PicklistId)
AttributeDefinition ← ProductAttributeDefinition (AttributeDefinitionId)
Product2 ← ProductAttributeDefinition (Product2Id)
Product2 ← ProductCategoryProduct (ProductId)
Product2 ← ProductRelatedComponent (ParentProductId, ProductId)
Product2 ← ProductSellingModelOption (Product2Id)
ProductCategory ← ProductCategoryProduct (CategoryId)
ProductRelationshipType ← ProductRelatedComponent (ProductRelationshipTypeId)
ProductSellingModel ← ProductSellingModelOption (ProductSellingModelId)
ProductClassification ← ProductClassification (ParentProductClassificationId, self-ref hierarchy)
ProductCategory ← ProductCategory (ParentCategoryId, self-ref hierarchy)
```

## SFDMU Data Plan: `qb-pcm`

28 objects loaded in dependency order. Root plan — must load before all other QB plans.

Key ordering: Attributes → Classifications → Products → SellingModels → Bundles → Catalogs → Qualifications

All products use `StockKeepingUnit` as externalId. Most objects use `Upsert` operation.
