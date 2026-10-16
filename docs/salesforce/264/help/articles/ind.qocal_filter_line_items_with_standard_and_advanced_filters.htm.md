---
article_id: ind.qocal_filter_line_items_with_standard_and_advanced_filters.htm
title: Manage Product Visibility with Filters
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_filter_line_items_with_standard_and_advanced_filters.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_user_experience_and_customization.htm
fetched_at: 2026-09-04
---

# Manage Product Visibility with Filters

Use predefined and advanced filters to control which quote or order line items appear in the line editor. Filtering helps sales representatives manage complex quotes by focusing on specific product groups or line item statuses.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management where Transaction Management is enabled
USER PERMISSIONS NEEDED
To use the Transaction Line Editor or Sales Transaction Line Editor:	

Manage Revenue Management

AND

Create Orders from Quotes permission set

AND

Price and Tax Calculation for Quoting

Predefined filters provide quick access to specific line categories, such as all lines, ramped lines, errored lines, or unconfigured lines. For more granular control, advanced filters provide up to 5 custom conditions based on fields from the Quote Line Item or Order Product objects. These conditions support various operators—such as Equals, Contains, or Greater Than—depending on the data type of the selected field. To target specific sections of a complex quote, apply these conditions to all groups or selected subgroups.

Filter quote or order line items to refine the list of visible products and streamline the quoting process:

Open the Sales Transaction Line Editor and click the filter icon.
Select a filter option based on your needs.
Select a predefined category: All Lines, Errored Lines, Ramped Lines, or Unconfigured Lines.
Select advanced filters to define custom conditions.
In the Advanced Filters panel, set the filter scope. For Filter by Group, select All Groups or specific groups.
Click Add Filter and define the condition by selecting a field, an operator, and a value.
NOTE
To filter by a field from a related record, select the field from the field list. Related record fields include the relationship field name in brackets, such as [Product ID] Product Name.
Advanced filters support fields from records directly related to the Quote Line Item or Order Line Item. Fields that require more than one relationship aren't available for filtering
Filter only by fields that are available to the line editor. If a field isn't listed, add it as a column in the line editor.
For picklist fields, select one or more picklist values.
Add up to 5 conditions and use Add Filter Logic with AND or OR operators to refine the results.
Save your changes.
NOTE
If you apply a field-level column filter and a predefined or advanced filter, the most recently applied filter takes precedence.
When advanced filters are applied, sorting applies only to the filtered results.
NOTE When you apply advanced filters, sorting applies only to the filtered results.
The line editor applies the filter and shows only the matching line items.
To clear the active filter, click Remove Filter. To clear all conditions in the panel, click Remove All.
Advanced Filter Operators
Select an operator to define how the system evaluates field values. Available operators vary by the field's data type.
