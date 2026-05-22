---
article_id: ind.pricing_define_prices_in_price_books.htm
title: Define Prices in Price Books
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_define_prices_in_price_books.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Define Prices in Price Books

A price book is essentially your company's master product catalog, containing a complete list of your products and services along with their specific selling prices.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To create and manage cost books:	Salesforce Pricing Design Time User

The main purpose of a price book is to ensure your sales team can provide consistent and accurate pricing for every customer. Businesses can maintain a standard, company-wide price book or create multiple, custom price books for different currencies, regions, or customer segments, giving them full control over their pricing strategy.

Price books work by directly connecting your products to your sales deals. When a sales representative creates a quote for a customer, they first select the appropriate price book. Then, as they add products to the deal, the correct price for each item is automatically pulled from the selected book. This simple connection streamlines the entire sales process, ensuring quotes are accurate and making it much easier to manage prices and forecast future revenue.

To ensure accurate pricing when creating a quote with bundled products, make sure all products in the bundle belong to the same price book.

Optional: Configure Price Book Page Layout

If you want to associate your price book to a cost book, you’ll need to configure your page layout to show the cost book entry field.

From the Object manager, search for and select the Price Book object.
Select Page Layouts, and then click Price Book Layout.
In the palette, click Fields.
Drag and drop the Cost Book field to the Price Book’s page layout.
Save your changes.
Create a Price Book

All Salesforce orgs include a predefined Standard Price Book. However, you can create and activate any number of custom price books based on your business needs. Once active, sales reps can select them when adding products to opportunities.

From App Launcher, find and select Price Management.
From the app navigation menu, select Price Books.
On the Price Books page, click New.
Give your price book a name.
If necessary, specify these details:
Provide a description.
Set a date range to determine the price book’s validity.
Set the price book as active.
Optionally, associate your price book with a cost book.
Save your changes.
Add Price Book Entries

A price book entry is the record of a product or service and its list price within a specific price book.

IMPORTANT You can’t change the product selling model after you associate it with a price book entry. If you migrate to Agentforce Revenue Management and want to update an existing price book entry, ask your Salesforce admin to raise a support ticket.
From App Launcher, find and select Price Management.
From the app navigation menu, select Price Books, and then select a price book.
Click the Price Book Entries tab.
Click New.
Specify these details.
Search for and select a product.
Search for and select a price book.
Enter a list price for your product.
If necessary, select the product selling model.
Save your changes.
