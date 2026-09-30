---
page_id: cml_best_practice_pcg_group_relations.htm
title: "PCG Group Relations: Follow Order in Constraints"
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_pcg_group_relations.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-09-29
---

# PCG Group Relations: Follow Order in Constraints

Order the Product Component Group (PCG) group relations in the way they appear in the
    constraints.

    

Order the Product Component Group (PCG) group relations in the way they appear in the
      constraints. Specify the groups used in the LHS of the constraints first, followed by those
      in the RHS.

    

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
