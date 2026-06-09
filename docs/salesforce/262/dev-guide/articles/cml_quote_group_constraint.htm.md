---
page_id: cml_quote_group_constraint.htm
title: Define a Constraint for a Quote Group
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_quote_group_constraint.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_quote_group_ramp_segment_constraints.htm
fetched_at: 2026-06-09
---

# Define a Constraint for a Quote Group

To define a constraint for a quote group, use the require rule to assign the
SalesTransactionItemGroup attribute that’s contained on a type to the value of the
QuoteGroup container.

In this example for a GeneratorSet and its Enclosure, all the relations defined in the
groupBy container include the `SalesTransactionItemGroup` attribute. Constraint Rules Engine creates a
virtual container for each unique value of the `SalesTransactionItemGroup` attribute defined in the `groupBy` container. The engine creates one virtual
container with its own self-contained rule execution for each group that contains one or
more of the products defined in the `QuoteGroup`
container.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

Groups don’t support rules such as Hide, Disable, or Recommend,
that perform an action when specified conditions are true.

## Example

```
type LineItem {
    @(tagName = "SalesTransactionItemGroup")
    string SalesTransactionItemGroup;
}

type GeneratorSet : LineItem;
type Enclosure : LineItem;

// Transaction scoped container
@(virtual = true)
type Quote {
    relation quotegroup : QuoteGroup;
    @(sourceContextNode = "SalesTransaction.SalesTransactionItem") relation generators : GeneratorSet;
    @(sourceContextNode = "SalesTransaction.SalesTransactionItem") relation enclosures : Enclosure;
}

// Group scoped container
@(virtual = true, groupBy = SalesTransactionItemGroup)
type QuoteGroup {
    string SalesTransactionItemGroup; // Needed for the require rule to save

    @(sourceContextNode = "SalesTransaction.SalesTransactionItem") relation generators : GeneratorSet;
    @(sourceContextNode = "SalesTransaction.SalesTransactionItem") relation enclosures : Enclosure;

    require(generators[GeneratorSet], enclosures[Enclosure] {SalesTransactionItemGroup = SalesTransactionItemGroup});
}
```
