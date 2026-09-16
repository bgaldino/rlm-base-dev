---
article_id: ind.product_catalog_create_a_unit_of_measure.htm
title: Create a Unit of Measure
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_create_a_unit_of_measure.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_decimal_quantity_support_in_product_catalog_management.htm
fetched_at: 2026-09-04
---

# Create a Unit of Measure

Capture accurate product quantities by defining the number of decimal places the product supports, with specific rounding methodologies.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To create a Unit of Measure:	DecimalQuantityDesigntime

For billing purposes, the system converts all units of measure in the unit of measure class to the default unit of measure. The conversion factor equates one unit of measure to another and helps with conversion. For example, for the Weight unit of measure class, the default unit of measure is pounds (lbs). Then, all units of measure records with the Weight unit of measure class are converted to equate 1 unit to 1 pound. If the unit of measure is kilogram, the conversion factor is 2.2 as 1 pound consists ‌of 2.2 kilograms.

From the App launcher, find and select Units of Measure.
Click New.
In the Unit of Measure field, find and select New Unit of Measure.
Enter a name for the unit of measure.

It's recommended to assign meaningful names as they'll be displayed to users.

Enter a unit code and type.
Here are some sample unit code and type values that you can enter.
SAMPLE UNIT CODE	SAMPLE TYPE
Length	meters, feet, inches, and centimeters
Weight	kilograms, pounds, and ounces
Volume	liters, gallons, and cubic meters
Time	seconds, minutes, and hours, days
Digital	bytes, kilobytes, and megabytes
Enter the scale.
The scale specifies the number of decimal places.
Select a rounding method.
Available rounding methods are Up, Down, and Nearest.
Save your changes.
