---
page_id: cml-set-product-selling-model-constraint
title: Set Product Selling Model in a Constraint
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-set-product-selling-model-constraint.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-constraints
legacy_page_id: cml_set_product_selling_model_constraint.htm
fetched_at: 2026-11-25
---

# Set Product Selling Model in a Constraint

Use the productSellingModel tagname to write a constraint that sets the Product Selling Model (PSM) for a type. You can define a PSM as one time, time-deferred (subscription with end date), or evergreen (recurring subscription with no preset end date). The PSM is updated for new line items at runtime, based on the constraint.

You can’t use a Constraint Modeling Language (CML) constraint to update the PSM for an existing quote line. For more information on product selling models, see [Manage Product Selling Model](https://help.salesforce.com/s/articleView?id=ind.product_catalog_product_selling_model.htm) in Revenue Cloud in Salesforce Help.

## Constraint Example

Using the `GeneratorSet` model, a constraint can be defined that sets the PSM based on a specific operational attribute chosen by the user, such as the `DutyRating`. This assumes that different duty ratings correspond to different billing models (for example, permanent installation versus temporary rental).

This example sets the PSM to a specific ID (for example, `PSM_EVERGREEN_ID`) if the user selects the “Continuous Power (COP)” duty rating.

```
//Global variable PSM ID
define PSM_EVERGREEN_ID "a00Tx000000Qz1g"
type GeneratorSet {
// Use the productSellingModel tag from the context definition
@(tagName = "ProductSellingModel")
string productSellingModel;
string DutyRating = ["Prime Power (PRP)", "Continuous Power (COP)", "Emergency Standby Power (ESP)"];
// Set PSM based on Duty Rating
constraint(
DutyRating == 'Continuous Power (COP)' ->    productSellingModel == PSM_EVERGREEN_ID
);
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-set-product-selling-model-constraint.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
