---
page_id: cml-best-practice-consolidate-defaults
title: Consolidate Multiple Default Configurations
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-consolidate-defaults.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-cml-best-practices
legacy_page_id: cml_best_practice_consolidate_defaults.htm
fetched_at: 2026-11-25
---

# Consolidate Multiple Default Configurations

Apply dynamic, overridable default quantities to a single component based on multiple states of a driving attribute, using one derived variable and a single setdefault rule.

Apply dynamic, overridable default quantities to a single component based on multiple possible states of a driving attribute. This process avoids rule conflicts where only the last rule evaluates.

When multiple `setdefault` rules target the same assignment in the RHS, evaluations can conflict. For example, a conflict can result when the rule targets the same relation and type, such as `accessories[Accessory] == ...`. The condition side can use different expressions, but if the rules resolve to the same target on the assignment side, behavior can become order-dependent and lead to inconsistent outcomes.

For example, if you want to set a default for the quantity of `Accessories` based on the selected `DutyRating` of a Generator Set, writing three separate `setdefault` rules causes inconsistent behavior depending on the quantity changes of the accessories.

To prevent the conflict, consolidate the conditional logic into a single derived variable using nested ternary expressions, such as `? :`. Then, apply a single `setdefault` rule using that newly derived variable to drive the relation’s quantity.

This example shows the recommended process, consolidating the logic into a single variable and rule.

```
type GeneratorSet : LineItem {
    string DutyRating = ["Prime Power (PRP)", "Continuous Power (COP)", "Emergency Standby Power (ESP)"];

    relation accessories : Accessory[1..99] {
        default Accessory(1);
    }

    // 1. Consolidate the conditional logic into a single integer variable
    int defaultAccessoryQty = (DutyRating == "Prime Power (PRP)") ? 2 : ((DutyRating == "Continuous Power (COP)") ? 4 : 6);

    // 2. Create a dynamic informational message
    string infoMsg = DutyRating + " accessory default overridden";

    // 3. Apply a single setdefault rule using the derived variable
    setdefault(
        DutyRating in ["Prime Power (PRP)", "Continuous Power (COP)", "Emergency Standby Power (ESP)"],
        accessories[Accessory] == defaultAccessoryQty,
        infoMsg
    );
}
```

Avoid the process shown in this example, which includes multiple conflicting `setdefault` rules.

```
type GeneratorSet : LineItem {
    string DutyRating = ["Prime Power (PRP)", "Continuous Power (COP)", "Emergency Standby Power (ESP)"];

    relation accessories : Accessory[1..99] {
        default Accessory(1);
    }

    // X AVOID: Multiple setdefault rules targeting the same relation.
    // Only the last rule will reliably evaluate.
    setdefault(DutyRating == "Prime Power (PRP)", accessories[Accessory] == 2, "PRP error");
    setdefault(DutyRating == "Continuous Power (COP)", accessories[Accessory] == 4, "COP error");
    setdefault(DutyRating == "Emergency Standby Power (ESP)", accessories[Accessory] == 6, "ESP error");
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-consolidate-defaults.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
