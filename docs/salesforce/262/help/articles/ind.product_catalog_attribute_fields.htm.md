---
article_id: ind.product_catalog_attribute_fields.htm
title: Working with Product Attribute Fields
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_attribute_fields.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Working with Product Attribute Fields

Learn more about the fields used in product attribute definitions. Some fields simply define an attributes, while others affect runtime when your sales reps are working with quotes and orders.

REQUIRED EDITIONS
View supported products and editions.
Attribute fields and descriptions
FIELD	DESCRIPTIONS
Name	The name of the attribute.
Product	The name of the product. This field is available when you edit inherited product attributes. This field isn’t editable.
Product Classification	The name of the product classification. This field is available when you edit the product classification attribute. This field isn’t editable.
Attribute	The attribute associated with the product classification or product. This field isn’t editable.
Attribute Category	The attribute category associated with the product classification or product. This field isn’t editable.
Status	The lifecycle status of the attribute.
Help Text	This field stores useful information for runtime users.
Default Value	The default value of an attribute for a product classification or product.
Attribute Name Override	The name that’s displayed for the product classification attribute or product attribute instead of the specified attribute name. The Attribute Name Override overrides the name on the attribute. For example, you can override the attribute “Color” to display as “Laptop Color” for a product classification or a product.
Value Description	The description of the value defined for the product classification attribute or the product attribute.
Description	The description of the product classification attribute or the product attribute.
Is Price Impacting	Select if this attribute dictates the price of a product.
Sequence	The display sequence of the attribute when you configure the attribute during runtime.
Minimum Value	The minimum value that you can enter for attributes of type number, currency, and percent in run time. The minimum value must be less than or equal to the maximum value.
Maximum Value	The maximum value that you can enter for attributes of type number, currency, and percent in run time.
Minimum Character Count	The minimum number of alphanumeric characters that you can enter for attributes of type number and text in run time. The minimum character count must be less than or equal to the maximum character count.
Maximum Character Count	The maximum number of alphanumeric characters that you can enter for attributes of type number and text in run time.
Run Time Settings
SETTING	DESCRIPTION
Is Required	Select the field if this attribute requires a value when you assign it to a parent object.
Is Hidden	Select the field if you want to hide the attribute from users in the run time.
Is ReadOnly	Select the field if the attribute is read only for users in the run time.
Display Type	Select how attributes of a specific data type are displayed in the user interface at run time. For example, attributes of a checkbox data type can be displayed as checkboxes or toggles in the user interface.
Step Value	You can display attributes of the currency, number, and percent data types as sliders in the user interface at run time. Instead of typing in a number, or using increment buttons, drag the slider on a predefined scale to adjust the attribute values. The slider is positioned at the default value. You can slide the attribute value in increments or decrements of the step value. The step value must be greater than zero. Additionally, the difference between the maximum value and minimum value must be exactly divisible by the step value. You must always define the default value, minimum value, and maximum value for an attribute when the attribute’s display type is slider.
Examples for run-time attribute settings
ATTRIBUTE	IS REQUIRED	IS HIDDEN	IS READ ONLY	RESULT
Color	Yes	No	Yes	This is a required attribute and is visible in the run time. It has a default value, however the value isn’t editable.
Quantity	Yes	No	No	This is a required attribute and is visible in the run time. It has a default value, and the value is editable.
Assembly Required	No	Yes	Yes or No	This is an optional attribute that isn’t visible in the run time.
Country of Origin	No	No	Yes	This is an optional attribute that’s visible in the run time. However, the attribute value isn’t editable.
Check Availability in Zip Code	No	No	No	This is an optional attribute that’s visible in the run time. The attribute value is editable, but it's not mandatory to enter a value.
Considerations while updating attribute field values
If you update attribute field values in the attribute definition, review and update the corresponding attribute values on the product classification attributes and product attributes.
If you update these attribute field values in the product classification attributes, review and update the corresponding attribute values on the product attributes.
If you update attribute field values in the product attributes, review and update the corresponding attribute value overrides in the context of any bundles the product is a part of.
