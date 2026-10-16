---
article_id: ind.um_create_units_of_measure.htm
title: Create Units of Measure
source_url: https://help.salesforce.com/s/articleView?id=ind.um_create_units_of_measure.htm&type=5&release=264
release: 264
release_name: Winter '27
area: usage
parent_article: ind.um_configure_usage_records.htm
fetched_at: 2026-09-07
---

# Create Units of Measure

A unit of measure quantifies the consumption of a usage resource. You can define units of measure to support a wide range of usage resources. For example, a unit of measure can be time-based, volume-based, transaction-based, or count-based.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create usage product grant binding policies:	Usage Management Designer
From the App Launcher, find and select Units of Measure.
Click New.
Enter a name, a unique identifier code, and a description.
The Unit Code field must exactly match the currency ISO code configured in your org settings, such as USD. Mismatched casing or spelling hides rate cards during selling without an error message.
To group the unit of measure under a class, select a unit of measure class.
If necessary, to show the unit of measure in a specific order in a list, enter a sequence number.
Enter a conversion factor that converts the value of the unit of measure into the default unit of measure of the unit of measure class.
Select a type of measurement.
You can add new values to the type picklist. See Add or Edit Picklist Values.
Select a status.
	
Draft	Indicates that this record is still open for modifications. This is the default value.
Active	Indicates that Usage Management is using this record for resource consumption calculations and you can make limited modifications.
Inactive	Indicates that the record is not in use.
Save your changes.
SEE ALSO
Create a Unit of Measure Class
