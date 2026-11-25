---
page_id: cml-best-practice-pcg-group-relations
title: "PCG Group Relations: Follow Order in Constraints"
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-pcg-group-relations.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-cml-best-practices
legacy_page_id: cml_best_practice_pcg_group_relations.htm
fetched_at: 2026-11-25
---

# PCG Group Relations: Follow Order in Constraints

Order the Product Component Group (PCG) group relations in the way they appear in the constraints.

Order the Product Component Group (PCG) group relations in the way they appear in the constraints. Specify the groups used in the LHS of the constraints first, followed by those in the RHS.

In this example, the order of PCG groups is incorrect as `Test1Group` is part of the LHS and should be declared first.

```
type TestParent : LineItem {
    Test2Group test2group;

    Test1Group test1group;

    constraint(test1group.testchild1[TestChild1] > 0 -> test2group.testchild2[TestChild2] == test1group.testchild1[TestChild1]);

}
```

This example shows the correct order of PCG groups, where `Test1Group` is declared first because it is part of the LHS.

```
type Test20260204Parent : LineItem {

    Test1Group test1group;
    Test2Group test2group;

    constraint(test1group.testchild1[TestChild1] > 0 -> test2group.testchild2[TestChild2] == test1group.testchild1[TestChild1]);

}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-pcg-group-relations.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
