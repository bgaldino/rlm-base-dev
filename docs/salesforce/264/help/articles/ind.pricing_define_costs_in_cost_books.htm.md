---
article_id: ind.pricing_define_costs_in_cost_books.htm
title: Define Costs in Cost Books
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_define_costs_in_cost_books.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_price_books_salesforce_pricing.htm
fetched_at: 2026-11-23
---

# Define Costs in Cost Books

A cost book acts as a detailed expense tracker for your products. Think of it as the place where you record every cost associated with creating or delivering a product or service. Within a cost book, you create individual entries for each specific expense, such as the cost of raw materials, manufacturing, or shipping. These detailed cost entries are then linked directly to the corresponding product in your catalog, giving you a clear, itemized view of what it truly costs to bring that item to market.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
USER PERMISSIONS NEEDED
To create and manage cost books:	Salesforce Pricing Design Time User

This cost information is the foundation for building a smart and profitable pricing strategy. Once you know the true cost of a product, you can move beyond guesswork and set selling prices that ensure a healthy profit margin or markup. This allows you to accurately analyze the profitability of each item you sell, helping you make informed decisions on everything from sales promotions to product development, and ultimately ensuring your business remains profitable.

IMPORTANT Cost book entries record product costs for tracking purposes only. You can't use this cost data on quotes or orders. Salesforce Pricing doesn't pull cost book entries into quote lines, and doesn't calculate margins or markups from them. Additionally, you can't reference cost book data directly in pricing procedures.
Example: Calculate Margin by Using a Standard Cost Book
Salesforce Pricing doesn't bring cost data into the quote line or calculate margin automatically. This example shows one way to surface cost on the quote line item and calculate margin from it, using standard Salesforce Pricing building blocks and custom fields.
Create a Cost Book
From App Launcher, find and select Price Management.
From the app navigation menu, select Cost Books.
On the Cost Books page, click New.
Give your cost book a name.
Set a date range to determine the cost book’s validity.
Optionally, you can designate a cost book as the default.
Save your changes.
Add Cost Book Entries

A cost book entry is each cost factor that is tracked as a product with the cost price.

From App Launcher, find and select Price Management.
From the app navigation menu, select Cost Books, and then select a cost book.
Under the Related tab, under Cost Book Entry, click New.
Search for and select a product.
Each cost factor is stored as a product record.
Enter the cost of the product.
Specify the cost currency.
Set the date range.
If necessary, enter a description.
Save your changes.
NOTE The cost book details are populated when you create the cost book entry from the cost book record. If you directly navigate to the Cost Book Entry page, you must associate the cost book entry with a cost book.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.pricing_define_costs_in_cost_books.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
