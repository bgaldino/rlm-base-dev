---
article_id: ind.product_catalog_considerations_while_assigning_attributes_to_product_classifications.htm
title: Considerations While Assigning Attributes to Product Classifications
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_considerations_while_assigning_attributes_to_product_classifications.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_assign_attributes_to_a_product_classification.htm
fetched_at: 2026-09-04
---

# Considerations While Assigning Attributes to Product Classifications

Here are a few scenarios you can run into when assigning attributes to product classifications.

ERROR	SCENARIO	REMEDIATION
We couldn’t assign the selected Attribute Categories to the Product Classification. Select a single category for attributes that are duplicated across categories.	No attributes have been assigned to the product classification so far. You’re now assigning attributes through attribute categories. The selected attribute categories have a few attributes in common.	Select one category that’s the preferred category for the common attributes and assign that category to the product classification. If the preferred category is different for multiple common attributes, resolve conflicts by first assigning individual common attributes to the product classification, and then by assigning the remaining attributes via an attribute category.
Some attributes from the attribute category were already assigned to this product classification. The unassigned attributes are now assigned to the product classification.	A few attributes (via some attribute categories) have already been assigned to the product classification. You’re now assigning more attributes through attribute categories. The selected attribute categories include attributes that have already been assigned to the product classification through other attribute categories. 	The attributes from the attribute category that weren’t already assigned to the product classification are now assigned to the product classification.
We couldn’t assign the selected attributes because they belong to more than one category. Select a single attribute to an attribute category combination.	A few attributes have already been assigned to the product classification. You’re assigning individual attributes to the product classification, but the selected attributes belong to more than one category. 	Select a single attribute to an attribute category combination and assign it to the product classification.
