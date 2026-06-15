---
page_id: cml_ramp_group_constraint.htm
title: Define a Constraint for a Ramp Group
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_ramp_group_constraint.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_quote_group_ramp_segment_constraints.htm
fetched_at: 2026-06-09
---

# Define a Constraint for a Ramp Group

To define a constraint that applies to a ramp group, use the IsLineGroupRamped\_\_std
attribute in the require rule to specify that the group is a ramp group.

In this example, the Enclosure is added to the group only if the GeneratorSet is in a ramp
group. In the last lines of the example, the `IsLineGroupRamped__std` attribute in the require rule specifies that the GeneratorSet
is in a ramp group.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

Groups don’t support rules such as Hide, Disable, or Recommend, that
perform an action when specified conditions are true.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

To add a type to an unramped group only and exclude the type from ramp
groups, set the `IsLineGroupRamped__std` attribute to NOT (!)
in the require rule. For example, `require(!(generators[GeneratorSet].IsLineGroupRamped__std),`.

## Example

```
type LineItem {
    @(tagName = "SalesTransactionItemGroup")
    string SalesTransactionItemGroup;
    @(tagName = "IsLineGroupRamped__std")
    boolean IsLineGroupRamped__std;
}

type GeneratorSet : LineItem;
type Enclosure : LineItem;

// Transaction scoped container
@(virtual = true) type Quote;

// Group scoped container
@(virtual = true, groupBy = SalesTransactionItemGroup)
type QuoteGroup {
    string SalesTransactionItemGroup; // Needed for the require rule to save

    @(sourceContextNode = "SalesTransaction.SalesTransactionItem") relation generators : GeneratorSet;
    @(sourceContextNode = "SalesTransaction.SalesTransactionItem") relation enclosures : Enclosure;

    require(generators[GeneratorSet].IsLineGroupRamped__std, enclosures[Enclosure] {SalesTransactionItemGroup = SalesTransactionItemGroup});
}
```
