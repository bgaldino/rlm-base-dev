---
article_id: ind.product_catalog_configure_product_attributes.htm
title: Configure Product Attributes in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_configure_product_attributes.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Configure Product Attributes in Agentforce Revenue Management

Products that are based on a product classification inherit all the attributes from the product classification. You can configure the inherited attributes to make them product-specific. You can override the configured and inherited attributes in the context of a product bundle.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To configure product attributes:	Manage Product Catalog
From the Product Catalog Management app’s home page, click Products.
From the product list view page, click the product.
Navigate to the Attributes tab.
To configure a product attribute that is inherited from the product classification, click  next to an inherited attribute, and then click Configure.
In the New Product Attribute Definition window, edit the fields as necessary.
To display attributes of currency, number, and percent data types as sliders at run time, configure product attributes of these data types and specify these details:
Select Slider under Display Type.
Enter a minimum value.
Enter a maximum value.
Enter a step value.
You can display attributes of the currency, number, and percent data types as sliders in the user interface at run time. Instead of typing in a number, or using increment buttons, drag the slider on a predefined scale to adjust the attribute values. The slider is positioned at the default value. You can slide the attribute value in increments or decrements of the step value. The step value must be greater than zero. Additionally, the difference between the maximum value and minimum value must be exactly divisible by the step value. You must always define the default value, minimum value, and maximum value for an attribute when the attribute’s display type is slider.
Enter a default value.
Save your changes.
EXAMPLE Consider an iPhone that has attributes such as model, color, and display. The iPhone has inherited all these attributes from the product classification Phones. When a user purchases this iPhone as part of the Apple phones product bundle, you want the iPhone to be available in red color by default. To create this configuration, you can override the default attribute value of color and set it to red for iPhone in the context of the Apple Phones bundle.
