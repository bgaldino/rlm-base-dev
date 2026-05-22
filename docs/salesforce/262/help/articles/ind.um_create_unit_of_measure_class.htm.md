---
article_id: ind.um_create_unit_of_measure_class.htm
title: Create a Unit of Measure Class
source_url: https://help.salesforce.com/s/articleView?id=ind.um_create_unit_of_measure_class.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Create a Unit of Measure Class

Unit of measure class defines the groupings of units of measure (UOM). For example, the Currency unit of measure class groups various currencies, such as euros, dollars, and rupees.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create a usage product grant binding policies:	Usage Management Designer

For billing purposes, all units of measure in a unit of measure class are converted to the default unit of measure. The conversion factor equates one unit of measure to another. For example, for the Weight unit of measure class, the default unit of measure is pounds (lb). Therefore, all records with the Weight unit of measure class are converted to equate one unit to 1 pound. If the unit of measure is kilograms, the conversion factor is 2.2 because 1 kilogram equals 2.2 pounds.

From the App Launcher, find and select Unit of Measure Classes.
Click New.
Enter a name, a unique identifier code, and a description.
If necessary, select a default unit of measure.
If you don’t select a default unit of measure, Salesforce uses the unit of measure within this class as the default unit for all conversions. If no unit of measure is available, create a new record.
Select a type.
	
Usage	For measuring consumption in non-currency units, such as API calls, GB, or hours.
Currency	For measuring consumption value in currency, such as USD or EUR.
Token	For measuring redeemable credits.
When you select a Unit of Measure, align the category with the Unit of Measure class. For example, the Data class uses the Usage category, with GB, MB, and TB as the units associated with the usage type. The Currency class includes units such as USD, INR, and EUR and requires the Currency category because it represents currency types.
Select a status.
	
Draft	Indicates that this record is still open for modifications. This is the default value.
Active	Indicates that Usage Management is using this record for resource consumption calculations and you can make limited modifications.
Inactive	Indicates that the record is not in use.
Save your changes.
SEE ALSO
Create Units of Measure
