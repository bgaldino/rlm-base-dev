---
article_id: ind.product_configurator_flow_product_attributes.htm
title: Product Attributes
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_flow_product_attributes.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Product Attributes

Product Attributes is the container component that shows product attributes in Product Configurator. The component organizes attributes by category and supports multiple display modes, including tabs, sections, and accordions. Product Attributes has no output properties and doesn’t listen to any events.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Product Attribute Responsibilities
Receive attributeCategories data from Data Manager
Support multiple display modes including tabs, sections, and accordions, and organize attributes by category
Render child components and creates attributeList components for each category
Publish Lightning Message Service (LMS) events and send attribute changes to Data Manager
Fire FlowAttributeChangeEvent for flow integration
Product Attributes API Name

S01_AttributesPanel

Input Properties

Product Attributes receives input from parent or flow components set by the customer.

PROPERTY	TYPE	REQUIRED	DESCRIPTION
attributes	Array	Yes	Array of attribute categories from DataManager
variant	String	No	Display mode: "tabs", "sections", "accordions", or "scoped"
categorize	String	No	Whether to categorize attributes: "true" or "false"
columns	String	No	Number of columns: "1" or "2"
uncatAttrsLabel	String	No	Label for uncategorized attributes
disabled	Boolean	No	Disables all attribute input fields, preventing users from editing any attribute values.
isApiInProgress	Boolean	No	Whether an API call is in progress
Events Product Attributes Fires

Product Attributes fires Lightning Message Service (LMS) events and FlowAttributeChange events.

Product Attributes fires the LMS event shown in this table.

EVENT ACTION	WHEN IS IT FIRED	PURPOSE
LMS_EVENTS.VALUE_CHANGE	User changes attribute value	Notify Data Manager of the changes

Product Attributes fires the FlowAttributeChange event shown in this table.

EVENT ACTION	WHEN IS IT FIRED	PURPOSE
FLOW_ATTRIBUTE_CHANGE	User changes attribute value	Notify flow of attribute change
