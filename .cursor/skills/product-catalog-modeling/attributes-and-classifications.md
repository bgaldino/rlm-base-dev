# Attributes and Classifications

> Sub-file of [`SKILL.md`](SKILL.md). Release 264. Read when deciding where an attribute
> lives and where its values are set. Source tags follow the parent skill's convention.

## The chain

```
AttributePicklist ─< AttributePicklistValue
        │ (PicklistId)
AttributeDefinition ─< AttributeCategoryAttribute >─ AttributeCategory
        │
ProductClassificationAttr  (classification level; parent → subclassification inherit)
        │  Product2.BasedOnId → ProductClassification
ProductAttributeDefinition (product level; OverrideContextId set = bundle-context override)
```

[Repo: `revenue-cloud-data-model/domains/pcm.md`; `scripts/ai/query_erd.py describe Product2`; Dev guide: `sforce_api_objects_productattributedefinition.htm`]

- **Picklists come first.** An attribute of type picklist needs its picklist to exist; a
  picklist can be reused by several attributes. Picklist value types: Boolean, Date,
  Datetime, Number, Text, Currency, Percent. [Help: `ind.product_catalog_picklists.htm`]
- **Classifications are the only way to give a product attributes.** A product is based on
  one classification (`Product2.BasedOnId`, a single lookup), which must be Active when you
  select it. [Help: `ind.product_catalog_product_classifications.htm`; `ind.product_catalog_create_bundled_products.htm`; Repo: ERD]
- **Subclassifications** inherit every parent attribute and may add their own: up to three
  levels, up to five children per node. [Help: `ind.product_catalog_product_classifications.htm`]
- **Attribute categories** group attributes for assignment. Assigning, to a classification
  with no attributes yet, several categories that share attributes fails. Assign the one
  category you prefer for the shared attributes, or, if the preferred category differs per
  attribute, assign the shared attributes individually first and the rest through categories. [Help: `ind.product_catalog_considerations_while_assigning_attributes_to_product_classifications.htm`]

## Designing the classification tree

| Choice | Trade-off | Downstream |
|---|---|---|
| Put an attribute on the **parent** classification | Defined once, inherited by every subclassification | An attribute-based adjustment cannot use an inherited attribute; selecting one fails validation on save. [Help: `ind.pricing_attribute_based_pricing_limits.htm`] |
| Put it on the **leaf** classification | Repeated across siblings | Usable by attribute-based pricing for that classification |
| One classification per product line | Simple, few rows | Every product of the line shares one attribute set; per-product differences need product-level configuration |
| Classification as a bundle **classification component** | The bundle offers "any product of this class" | Group, not the class, limits how many; class membership changes do not reach CML. [Help: `ind.product_configurator_sync_cml_and_pcm.htm`] |

**Rule of thumb:** a **price-impacting** attribute belongs directly on the classification
or subclassification the adjustment names, not on a parent it inherits from. Put purely descriptive or shared
configuration attributes higher. [Help: `ind.pricing_attribute_based_pricing_limits.htm`]

## Four places a value can be set

| Level | Object | Typical use |
|---|---|---|
| Attribute definition | `AttributeDefinition` (`DefaultValue`, `IsRequired`) | The attribute's global defaults |
| Classification attribute | `ProductClassificationAttr` | Defaults, required, hidden, read-only, excluded picklist values for every product of the class |
| Product attribute | `ProductAttributeDefinition` (no `OverrideContextId`) | One product's configuration of an inherited attribute |
| Bundle-context override | `ProductAttributeDefinition` with `OverrideContextId` = root bundle | The product's attribute inside one bundle only |

[Help: `ind.product_catalog_configure_product_attributes.htm`; `ind.product_catalog_override_product_component_attributes_in_bundles.htm`; Dev guide: `sforce_api_objects_productattributedefinition.htm`, `sforce_api_objects_productclassificationattr.htm`]

Shared fields at the classification, product and override levels: `AttributeNameOverride`
(display name, e.g. Colour shown as "Laptop Colour"), `DefaultValue`, `IsRequired`,
`IsHidden`, `IsReadOnly`, `IsPriceImpacting`, `DisplayType`, min/max value and character
count, `StepValue`, `Sequence`, `Status`. Booleans default `false`; `Status` defaults to
`Draft`. The definition level carries only `DefaultValue` and `IsRequired` of these.
[Help: `ind.product_catalog_attribute_fields.htm`; Dev guide: `sforce_api_objects_productclassificationattr.htm`, `sforce_api_objects_attributedefinition.htm`]

**Changes do not cascade for you.** After changing a definition, review the classification
attributes; after changing a classification attribute, review the product attributes; after
changing a product attribute, review its bundle overrides. [Help: `ind.product_catalog_attribute_fields.htm`]

**Picklist narrowing.** Every picklist value is included by default at classification
level; exclude values there, at the product, or in a bundle override
(`ExcludedPicklistValues` on the classification attribute). [Help: `ind.product_catalog_include_or_exclude_picklist_values_in_a_product_classification_attribute.htm`; `ind.product_catalog_products.htm`; `ind.product_catalog_create_bundled_products.htm`; Dev guide: `sforce_api_objects_productclassificationattr.htm`]

### Bundle-context overrides: use sparingly

- An override applies to **every instance** of that product in the bundle. [Help: `ind.product_catalog_override_product_component_attributes_in_bundles.htm`]
- The pricing engine **does not** apply attribute-based adjustments to an attribute with an
  overridden bundle context. Define a price-impacting attribute once; do not override it.
  [Help: `ind.pricing_attribute_based_pricing_limits.htm`]
- A static bundle needs a default for every attribute of every component. [Help: `ind.product_catalog_change_a_configurable_bundle_product_to_a_static_bundle_product.htm`]

## Run-time settings

| `IsRequired` | `IsHidden` | `IsReadOnly` | Effect |
|---|---|---|---|
| on | off | on | Visible, has a default, cannot be edited |
| on | off | off | Visible, must have a value, editable |
| off | on | any | Not shown |
| off | off | on | Visible, optional, not editable |

Sliders: Currency/Number/Percent with `DisplayType = Slider`; step > 0, and (max − min) must
divide exactly by the step; default, min and max are all required. [Help: `ind.product_catalog_attribute_fields.htm`; `ind.product_catalog_configure_product_attributes.htm`]

## What pricing and configuration rules need

**Attribute-based pricing** (Help: `ind.pricing_attribute_based_pricing_limits.htm`):

- Only active attributes with Is Price Impacting selected. (Help: `ind.pricing_define_price_impacting_attributes.htm`)
- Only attributes assigned directly to the selected classification or subclassification.
- No picklist over a Boolean data type; use a Checkbox/Boolean attribute.
- Numeric values match in the `.0` form (10 is stored as 10.0).
- No bundle-context override on the attribute.

**Configuration rules (CML)** see attributes as variables. Sync carries attribute deletion,
deactivation, value add/remove and default changes, but **not** attributes under a product
class, or newly added attributes. [Help: `ind.product_configurator_sync_cml_and_pcm.htm`]
Adding an attribute a rule must read is therefore a CML change too (`constraint-models`).

## Loading attributes

Measured on a 264 build of one PCM plan (for the QuantumBit plan this is open; see [`SKILL.md`](SKILL.md#loading-the-model)): after the **first** SFDMU insert on a fresh org,
classification attributes' `AttributeNameOverride` and `IsRequired` held platform defaults;
a second, update pass applied the plan's values. [Measured: 2026-11, 264] Load twice, and
do not extract from an org that had one pass. Traced explanation: on **insert** of a classification attribute the platform copies the attribute definition's `IsRequired`, `DefaultValue`, descriptions, help text and name into the new row (overwriting a supplied value when the definition's is valid), except for a row that overrides an inherited attribute; an **update** copies nothing, so the stored values stay and a later pass does not reset them. No equivalent copy was found for `ProductAttributeDefinition`. [Platform behaviour, traced] `IsComponentRequired` and `MinBundleComponents` take no value from a definition: no default-on-insert was found for them (see [`bundles-and-cardinality.md`](bundles-and-cardinality.md#two-kinds-of-cardinality)). Whether other classification-attribute fields
behave the same is **Open — needs live verification**.

`ProductAttributeDefinition.AttributeCategoryId` and `ProductClassificationAttr.AttributeCategoryId`
are create-only: a row first inserted without its category keeps it blank on reload.
[Repo: `sfdmu-data-plans/SKILL.md` → *Reloading a Plan Into a Live Org*]
