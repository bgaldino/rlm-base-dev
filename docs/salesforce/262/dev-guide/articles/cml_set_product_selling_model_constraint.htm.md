---
page_id: cml_set_product_selling_model_constraint.htm
title: Set Product Selling Model in a Constraint
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_set_product_selling_model_constraint.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_constraints.htm
fetched_at: 2026-06-09
---

# Set Product Selling Model in a Constraint

Use the productSellingModel tagname to write a constraint that sets the Product Selling
Model (PSM) for a type. You can define a PSM as one time, time-deferred (subscription with end
date), or evergreen (recurring subscription with no preset end date). The PSM is updated for new
line items at runtime, based on the constraint.

You can’t use a Constraint Modeling Language (CML) constraint to update the PSM for an
existing quote line. For more information on product selling models, see [Manage Product Selling Model](https://help.salesforce.com/s/articleView?id=ind.product_catalog_product_selling_model.htm&language=en_US "HTML (New Window)")
in Revenue Cloud in Salesforce Help.

## Constraint Example

Using the `GeneratorSet` model, a constraint can be
defined that sets the PSM based on a specific operational attribute chosen by the user, such
as the `DutyRating`. This assumes that different duty
ratings correspond to different billing models (for example, permanent installation versus
temporary rental).

This example sets the PSM to a specific ID (for example, `PSM_EVERGREEN_ID`) if the user selects the "Continuous Power (COP)"
duty rating.

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
