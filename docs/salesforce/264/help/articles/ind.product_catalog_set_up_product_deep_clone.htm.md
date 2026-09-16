---
article_id: ind.product_catalog_set_up_product_deep_clone.htm
title: Set Up Product Deep Cloning
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_set_up_product_deep_clone.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_deep_clone_in_product_catalog_management.htm
fetched_at: 2026-09-04
---

# Set Up Product Deep Cloning

Customize the product deep clone settings to add the appropriate context definition and expression set.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To set up a product deep clone:	Product Designer
From Setup, in the Quick Find Box, enter Deep Clone Product Settings, and select it.
Select the required context definition and expression set.

You can choose only the ProductDeepCloneContext context definition or a context definition extended from ProductDeepCloneContext.

ProductDeepCloneContext is available as the default context definition. You can extend the ProductDeepCloneContextcontext definition to add standard or custom fields and objects.

Always define context tags on relationship nodes, not on canonical nodes. When performing ExpressionSet calculations, reference context tags from these relationship nodes.

EXAMPLE

Scenario 1: Include a custom field.

You have a custom field on a Product X and want it included in the deep-cloned product, you need to include this custom field in the product X deep clone definition. Extend the product X deep clone definition to include the custom field. Make sure to map this field to the corresponding SObject field in the context mapping.

Scenario 2: Include an extended object.

You have an extended object related to Product X and want to include it in the deep cloned product, extend the product X deep clone definition to include the extended object. Define the appropriate relationship mapping between the two objects within the context definition. Include the fields of the extended object that you want to deep clone.

Scenario 3: Modify field values.

If the current product has a date field set to "TODAY," and you want the cloned product to have a date field set to "TODAY + 10 days," you can define a rule within the expression set to achieve this. Further, the date field must be present in the context definition and must have a context tag defined.
