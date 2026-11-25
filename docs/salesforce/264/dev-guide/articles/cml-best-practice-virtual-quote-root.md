---
page_id: cml-best-practice-virtual-quote-root
title: "Virtual Quote Root: Model Cross-Bundle Logic Using a Shared Transaction Parent"
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-virtual-quote-root.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-cml-best-practices
legacy_page_id: cml_best_practice_virtual_quote_root.htm
fetched_at: 2026-11-25
---

# Virtual Quote Root: Model Cross-Bundle Logic Using a Shared Transaction Parent

For transaction-level rules that span products that have no parent-child relationship, use a virtual quote as a transaction root pattern.

For transaction-level rules that span products that have no parent-child relationship, use a virtual quote as a transaction root pattern. Define a virtual type that exists only to act as the configuration root. Each independent bundle or standalone product hangs off it as a relation. Because the products share the virtual root as a common parent, a rule declared on the virtual root can reach across both subtrees to give cross-bundle interaction logic.

In this example, `GeneratorSet` is a bundle with its own `Accessories` child hierarchy, and `InstallationKit` is an independent standalone product. The `require` rule ties them together at the transaction level, so that any generator that includes accessories must also ship with an installation kit.

```
// Child line inside the GeneratorSet bundle
type Accessory;

// An independent standalone product
type InstallationKit;

// The GeneratorSet bundle owns its own child hierarchy
type GeneratorSet {
    int requiredKW = [101..10000];
    relation Accessories : Accessory[0..99];
}

// Virtual transaction root: never sold on its own. It exists only to
// host cross-bundle rules by giving independent products a shared parent.
type Quote {
    relation generatorSet    : GeneratorSet[0..1];
    relation installationKit : InstallationKit[0..1];

    /**
    * @Title Cross-Bundle Attach Rule
    * When the GeneratorSet includes at least one Accessory, the
    * transaction must also include exactly one Installation Kit.
    */
    require(
        generatorSet.Accessories[Accessory] > 0,
        installationKit[InstallationKit] == 1,
        "An Installation Kit is required when the GeneratorSet includes accessories"
    );
}
```

`generatorSet.Accessories[Accessory] > 0` is the condition, which reaches down into the subtree of `GeneratorSet` to count the `Accessory` lines. `installationKit[InstallationKit] == 1` is the target, which acts on a completely separate branch of the transaction, forcing exactly one installation kit. The rule lives on `Quote`, not on `GeneratorSet` or `InstallationKit`, because only the shared root can see both branches at once. `GeneratorSet` and `InstallationKit` stay independent and sellable on their own, while the transaction-level relationship is layered on top only where they’re combined.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-virtual-quote-root.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
