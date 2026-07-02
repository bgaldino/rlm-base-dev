---
article_id: ind.qocal_filter_line_items_with_standard_and_advanced_filters.htm
title: Manage Product Visibility with Filters
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_filter_line_items_with_standard_and_advanced_filters.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Manage Product Visibility with Filters

Use predefined and advanced filters to control which quote or order line items appear in the line editor. Filtering helps sales representatives manage complex quotes by focusing on specific product groups or line item statuses.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management where Transaction Management is enabled
USER PERMISSIONS NEEDED
To use the Transaction Line Editor or Sales Transaction Line Editor:	

Manage Agentforce Revenue Management

AND

Create Orders from Quotes permission set

AND

Price and Tax Calculation for Quoting

Predefined filters provide quick access to specific line categories, such as all lines, ramped lines, errored lines, or unconfigured lines. For more granular control, advanced filters provide up to five custom conditions based on fields from the Quote Line Item or Order Product objects. These conditions support various operators—such as Equals, Contains, or Greater Than—depending on the data type of the selected field. To target specific sections of a complex quote, apply these conditions to all groups or selected subgroups.

Filter quote or order line items to refine the list of visible products and streamline the quoting process:

Open the Sales Transaction Line Editor and click the filter icon.
Select a filter option based on your needs.
Select a predefined category: All Lines, Errored Lines, Ramped Lines, or Unconfigured Lines.
Select advanced filters to define custom conditions.
Select the filter scope by turning on Apply Filter to All Groups or selecting Selected Groups.
Click Add Filter and define the condition by selecting a field, an operator, and a value.
NOTE Use formula fields to filter values from related objects, as relationship fields like Product Name are unavailable.
Add up to five conditions and use Add Filter Logic with AND or OR operators to refine the results..
Save your changes.
NOTE If you use both field-level column filters and predefined or advanced filters, the last filter applied takes precedence.
Click Remove Filters or Remove All to clear active conditions.
Advanced Filter Operators
Select an operator to define how the system evaluates field values. Available operators vary by the field's data type.
