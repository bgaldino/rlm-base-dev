---
article_id: ind.pricing_price_propagation.htm
title: Price Propagation
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_price_propagation.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Price Propagation

Enable complex, hierarchical pricing logic by propagating values across different levels of a transaction from line items to groups and back. Use the Price Propagation element to perform sequential calculations and roll up totals from children to parents.

Key capabilities in Price Propagation

Price Propagation handles nested structures where a change at one level automatically updates related levels. Unlike standard bundle pricing, propagation supports flexible relationships between entities, such as group-to-group or group-to-item.

Horizontal Propagation: Calculate fields sequentially within a single line or group. For example, ensuring Net Price is calculated only after unit cost and margin are determined.
Ascending Propagation (Rollup): Aggregate values from child lines to parent groups. For example, calculating a Group Total by summing the Net Price of all items in that group.
Example of Group-to-Item Hierarchy

This example illustrates a multilevel hierarchy where the building node acts as the top-level parent, containing nested subgroups for floors and rooms and the corresponding line items.

Building (Group)
Floor (Subgroup)
Room (Subgroup)
Panel 001 (Line Item)
Panel 002 (Line Item)
Key Terms Used in Price Propagation
TERM	EXPLANATION	EXAMPLE
Group	A parent entity used to group and organize related quote line items.	Building (a group containing Floors and Rooms).
Subgroup	A group nested within another group, allowing multilevel structures in a quote.	Floor (subgroup under Building), Room (subgroup under Floor).
Node	A data source added in the propagation setup representing a specific level of data.	SalesTransactionItem (representing Panel 001), SalesTransactionGroup (representing Building).
Attribute	A field or a context tag on a node that can be used in formulas.	Net Price, Cost, Discount of Panel 001.
Merged Attribute	A unified column name created to map data between parent and child nodes for calculation.	MergedTotalCost (used to roll up Panel costs into the Room/Building cost).
Horizontal Calculation	Formulas applied sequentially within the same line or group level.	Panel Net Price = List Price – Discount
Ascending Propagation	The flow of values upward by rolling up totals from children to parent groups.	The Net Price of Panel 001 and Panel 002 rolls up to calculate the room total, which rolls up to floor, and then the building.
Add Nodes	Action to bring in data sources and their attributes into the propagation table.	Add the SalesTransactionItem node to access the Net Price of the Panel.
Join Nodes	Action to create relationships between nodes by using ID fields.	Join Room (Child Group) with Panel (Line Item) using a Parent ID to establish hierarchy.
Sequence	A mandatory numeric value that determines the strict order in which horizontal formulas are calculated.	Assign Sequence 1 to Panel Net Price, ensure it's calculated before it is used in Sequence 2 to calculate the Panel Margin.
Price Propagation Limits
Before adding the Price Propagation element to your pricing procedure, keep these points in mind:
Configure the Price Propagation Element
Define the formulas and execution sequence for your hierarchical pricing logic by using the Price Propagation element.
