---
article_id: ind.dro_comptibility_for_field_and_attributes_mapping.htm
title: Data Type Compatibility for Field and Attribute Mapping
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_comptibility_for_field_and_attributes_mapping.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_define_field_and_attribute_mapping.htm
fetched_at: 2026-09-05
---

# Data Type Compatibility for Field and Attribute Mapping

When you map a source attribute or field to a target attribute or tag, Dynamic Revenue Orchestrator (DRO) validates that the source and target data types are compatible. If they aren't compatible, the mapping can't be created.

REQUIRED EDITIONS
Available in: Salesforce Classic (not available in all orgs) and Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions

This table lists the supported target data types for each source data type.

Supported Source-to-Target Data Type Mappings
SOURCE DATA TYPE	SUPPORTED TARGET DATA TYPES
String (Context Tag)	String, Text
Text (Product Attribute)	String, Text
Date/Time	Date/Time, Date, String, Text
Date	Date, datetime, String, Text
Boolean (Context Tag)	Boolean, Checkbox, String, Text
Checkbox (Product Attribute)	Boolean, Checkbox, String, Text
Picklist	Picklist, String, Text
Currency	Currency, String, Text, Number
Number	Number, String, Text, Currency
Percent	Percent, String, Text
A context tag's String corresponds to a product attribute's Text datatype, and a context tag's Boolean corresponds to a product attribute's Checkbox. You can map between these equivalent types.
Any data type that isn't listed in the table can map only to the same data type, or to String or Text.
SEE ALSO
Define Field and Attribute Mapping
