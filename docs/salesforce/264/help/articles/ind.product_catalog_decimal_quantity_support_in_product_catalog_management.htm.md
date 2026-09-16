---
article_id: ind.product_catalog_decimal_quantity_support_in_product_catalog_management.htm
title: Decimal Quantity Support in Product Catalog Management
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_decimal_quantity_support_in_product_catalog_management.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_products.htm
fetched_at: 2026-09-04
---

# Decimal Quantity Support in Product Catalog Management

Define accurate product quantities for products that support decimal values. Based on the product's unit of measure (UOM), define the number of decimal places the product supports, with specific rounding methodologies.

REQUIRED EDITIONS
View supported products and editions.

Accurately measure product quantities in different units of measure, such as grams, kilograms, meters, feet, seconds and minutes. Each unit of measure belongs to a particular class, such as weight, height, and size. The decimal quantity of product values honors the scale or rounding methodology defined on the unit of measure. You can specify the decimal value and rounding methodologies for product quantities based on their UOM.

Using decimal quantities to define products makes product management more effective, especially in industries such as processing, manufacturing, and healthcare, where precise measurements are crucial.

EXAMPLE

In manufacturing and processing industry, accurate decimal quantities are critical. For example, a metal fabrication bundle may require 2.558 meters of steel, 1.25 kg of welding wire, and 0.8 liters of coating. Accurately managing these quantities ensures product quality, minimizes waste, and optimizes resource utilization.

Pharmacies and healthcare providers often manage fractional dosages like 0.5 tablets or 1.75 ml. Ability to handle accurate decimal quantities are crucial for patient safety and treatment efficacy.

Scaling and Rounding Methodology

Optimize numerical data by reducing the number of decimal places. Scaling specifies the limit on the number of decimal places and the rounding methodology adjusts the number accordingly. The rounding methods available are Up, Down, and Nearest.

NOTE

The value of scale must be greater than or equal to zero. If the scale is defined, then defining the rounding method is required, and vice versa.

If you receive an error when entering decimal values for quote line item quantities, verify that the DecimalQuantityDesigntime permission set is assigned and that the product has a unit of measure defined. For more details, see How to Update Quote Line Item Quantity with Decimal Values.

EXAMPLE



ROUNDING METHOD


	


EXAMPLE





​​Up: If the number of decimals in the original value exceeds the specified scale, this method rounds up the final decimal within the specified scale to the next higher value.

.	

Number = 2.54632

Scale = 3

Final = 2.547.

Here, the value of the third decimal place is increased to the next higher value.




Down: If the number of decimals in the original value exceeds the specified scale, this method retains the value of the final decimal within the specified scale.

	

Number = 2.54632

Scale = 3

Final = 2.546.

Here, the value of the third decimal place didn't change.




Nearest: If the number of decimals in the original value exceeds the specified scale, this method either rounds up the final decimal within the specified scale to the next higher value, or retains the value of the final decimal within the specified scale.

	

Number = 2.54632

Scale = 3

Final = 2.546.

Here, the value of the third decimal place didn't change because the value of the fourth decimal place was less than or equal to four.

Number = 2.54689

Scale = 4

Final = 2.5469.

Here, the value of the fourth decimal place is increased because the value of the fifth decimal place is greater than or equal to five.

Create a Unit of Measure
Capture accurate product quantities by defining the number of decimal places the product supports, with specific rounding methodologies.
SEE ALSO
View and Edit Quotes in Revenue Cloud
View and Edit Orders in Revenue Cloud
Unit Of Measure Inheritance and Rounding Values
