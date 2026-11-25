---
page_id: cml-quote-group-ramp-segment-constraints
title: Define Constraints for Quote Groups, Ramps, and Ramp Segments
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-quote-group-ramp-segment-constraints.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-types
legacy_page_id: cml_quote_group_ramp_segment_constraints.htm
fetched_at: 2026-11-25
---

# Define Constraints for Quote Groups, Ramps, and Ramp Segments

Apply rules to quote groups, ramps, and ramp segments by using the SalesTransactionItemGroup context tag. Assign a groupby value to messages defined in Constraint Rules Engine to include the messages in custom grouping strategies.

- 

**[Define a Constraint for a Quote Group](#define-a-constraint-for-a-quote-group)**

To define a constraint for a quote group, use the require rule to assign the SalesTransactionItemGroup attribute that’s contained on a type to the value of the QuoteGroup container.

- 

**[Define a Constraint for a Ramp Group](#define-a-constraint-for-a-ramp-group)**

To define a constraint that applies to a ramp group, use the IsLineGroupRamped__std attribute in the require rule to specify that the group is a ramp group.

- 

**[Define a Constraint for a Ramp Segment](#define-a-constraint-for-a-ramp-segment)**

To define a rule that applies to a ramp segment for defined conditions, use the ItemSegmentType attribute.

## Define a Constraint for a Quote Group

To define a constraint for a quote group, use the require rule to assign the SalesTransactionItemGroup attribute that’s contained on a type to the value of the QuoteGroup container.

In this example for a GeneratorSet and its Enclosure, all the relations defined in the groupBy container include the `SalesTransactionItemGroup` attribute. Constraint Rules Engine creates a virtual container for each unique value of the `SalesTransactionItemGroup` attribute defined in the `groupBy` container. The engine creates one virtual container with its own self-contained rule execution for each group that contains one or more of the products defined in the `QuoteGroup` container.

**Note:**

Groups don’t support rules such as Hide, Disable, or Recommend, that perform an action when specified conditions are true.

### Example

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

## Define a Constraint for a Ramp Group

To define a constraint that applies to a ramp group, use the IsLineGroupRamped__std attribute in the require rule to specify that the group is a ramp group.

In this example, the Enclosure is added to the group only if the GeneratorSet is in a ramp group. In the last lines of the example, the `IsLineGroupRamped__std` attribute in the require rule specifies that the GeneratorSet is in a ramp group.

**Note:**

Groups don’t support rules such as Hide, Disable, or Recommend, that perform an action when specified conditions are true.

**Note:**

To add a type to an unramped group only and exclude the type from ramp groups, set the `IsLineGroupRamped__std` attribute to NOT (!) in the require rule. For example, `require(!(generators[GeneratorSet].IsLineGroupRamped__std),`.

### Example

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
@(virtual = true) type Quote {
relation quotegroup : QuoteGroup;
}

// Group scoped container
@(virtual = true, groupBy = SalesTransactionItemGroup)
type QuoteGroup {
    string SalesTransactionItemGroup; // Needed for the require rule to save

    @(sourceContextNode = "SalesTransaction.SalesTransactionItem") relation generators : GeneratorSet;
    @(sourceContextNode = "SalesTransaction.SalesTransactionItem") relation enclosures : Enclosure;

    require(generators[GeneratorSet].IsLineGroupRamped__std, enclosures[Enclosure] {SalesTransactionItemGroup = SalesTransactionItemGroup});
}
```

## Define a Constraint for a Ramp Segment

To define a rule that applies to a ramp segment for defined conditions, use the ItemSegmentType attribute.

In this example, Enclosure is included in the group with GeneratorSet only if `ItemSegmentType` for GeneratorSet isn’t Trial. To set a value for `ItemSegmentType`, the type must be in a ramp group and be ramped.

**Note:**

Groups don’t support rules such as Hide, Disable, or Recommend, that perform an action when specified conditions are true.

### Example

```
type LineItem {
@(tagName = "SalesTransactionItemGroup")
string SalesTransactionItemGroup;
@(tagName = "ItemSegmentType")
string ItemSegmentType;
}

type GeneratorSet : LineItem;
type Enclosure : LineItem;

// Transaction scoped container
@(virtual = true) type Quote {
relation quotegroup : QuoteGroup;
}
// Group scoped container
@(virtual = true, groupBy = SalesTransactionItemGroup)
type QuoteGroup {
string SalesTransactionItemGroup; // Needed for the require rule to save

@(sourceContextNode = "SalesTransaction.SalesTransactionItem") relation generators : GeneratorSet;
@(sourceContextNode = "SalesTransaction.SalesTransactionItem") relation enclosures : Enclosure;

require(generators[GeneratorSet].ItemSegmentType != "Trial", enclosures[Enclosure] {SalesTransactionItemGroup = SalesTransactionItemGroup});
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-quote-group-ramp-segment-constraints.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
