---
article_id: ind.qocal_understand_usage_selling_rate_cards.htm
title: Set Up Rates for Usage-Based Products
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_understand_usage_selling_rate_cards.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Set Up Rates for Usage-Based Products

When you sell a usage-based product, the rate definitions and the rating discovery procedure that you set up in rate management retrieves the rate for these products. These rates are available with the product details when you browse the product catalog.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Configure Rate Cards and Rate Card Entries

Rate cards define the type of rate that you want to set for the service. A base-type rate card defines the standard per-unit cost, whereas a tier— or adjustment-type rate card defines a discounted price based on the defined tiers or volume. For more information, see Create a Rate Card Entry For Tier Rate Cards.

To define the actual rate, standard or discounted, applicable to a service, use rate card entries. These rate card entries contain the actual financial data ($1 per minute). You can mark the entries as negotiable, allowing sales reps to update the rate during the selling process.

NOTE The rate defined in the rate card entries is applicable only if these entries are set to Active. If they’re Draft or Inactive, the corresponding rates won’t appear.
Configure Tier Rate Cards for Commitment-Based Usage Products

In a commitment-based business model, tier rate cards determine how discounts apply on the volume, quantity, or monetary spend a customer has promised to consume.

To apply a resource-specific discount, create a rate card entry and specify a usage resource, such as Compute Hours or API Calls. Whereas to create a blanket discount that’s common across a user's entire account, leave the usage resource field empty.

EXAMPLE

Token Commitment—you can configure both, blanket or resource-specific discounts.

Blanket discount—A customer commits to consuming 1,000 tokens. You configure a "Token Commitment Flat" product that applies a flat discount of 10% across all usage resources. In this scenario, you leave the usage resource field empty. Therefore, every resource tied to the commitment receives the 10% discount.
Resource-specific discount—A customer commits to 5,000 tokens. Instead of a flat rate, you configure tier adjustments where you select the rates for each resource separately. In this scenario, you can select the usage resource for which you want the discount to apply. For example, you can define that their token commitment grants them a 30% discount specifically on DB Storage, while other resources might receive a different discount or no discount at all. You can also select a token resource while creating a rate card entry to provide a discount on tokens.

Monetary Commitment—similar to token commitments, you can configure both, blanket or resource-specific discounts.

Blanket discount—A customer agrees to spend $10,000. You configure a "Monetary Commitment Flat" product that applies a flat discount of 10% across all usage resources. In this scenario, you leave the usage resource field empty. Therefore, every resource tied to the commitment receives the 10% discount.
Resource-specific discount: A customer agrees to spend $5,000 in exchange for special rates. When setting up the tier adjustments, you can use the Is Included checkbox to specify the resources that benefit from the discount. For example, you can set up a 5% discount for Compute Time and a 10% discount for DB Storage, marking both as included. If you don’t mark a resource, such as Text Messages as included, it doesn’t benefit from the monetary commitment and is charged at the standard, undiscounted rate.

Quantity Commitment—quantity commitments are resource-specific, as the customer promises to consume a specific quantity of a usage resource.

Resource-specific discount: A customer commits to consuming 1,000 GB of DB Storage and 1,000 minutes of Compute Time. So, you define specific tier rate card entries for each resource. A 20% discount for every unit of DB Storage consumed, and a 10% discount for every minute of Compute Time consumed. As long as the customer doesn’t exceed their 1,000-unit limit for each respective resource, the discounted rates apply.
Map Rate Card to Price Books

When a sales rep creates a quote and selects a price book, make sure that you’ve linked the selected price book to the applicable rate card. Otherwise, the usage selling process can’t retrieve accurate rates applicable to a service.

Activate the Rating Discovery Procedure

Make sure that you select the applicable Rating Discovery Procedure in Revenue Settings. The selected procedure fetches the correct rates and discounts during the quoting process. For more information, see Select Rating Discovery Procedure.

EXAMPLE

Here are some use cases on how we can set up rate cards for our usage products.

For a standard mobile plan, the setup looks like this:

PRODUCT	RESOURCE	UOM	RATE UOM	RATE	NOTE
Mobile Plan	Text Messages	Count	USD	0.75	Text Messages are counted per message, and Data is measured per GB. Both are rated in USD.
Data	GB	USD	1.25

Calculating your bill: After the customer consumes the service, the system calculates their final charge based on the overage, which is the amount of usage that goes beyond any grants included in their plan. The system then applies the rate to that overage quantity. Here's how the charges are calculated based on your consumption:

Data: The customer consumed 102 GB. Because the plan includes a 2-GB grant, payment is only for the 100-GB overage (102 - 2 = 100). At a rate of $1.25 per GB, the charge is $125 (100 x $1.25).
Text Messages: The customer consumed 4500 messages. With a 4000 message grant, there’s a 500 message overage (4500 - 4000 = 500). At a rate of $0.75 per message, your charge is $375 (500 x $0.75).

For a mobile token-based plan, here's how the setup looks:

PRODUCT	RESOURCE	UOM	RATE UOM	RATE
Mobile Plan	Tokens	Each	USD	0.75
Text Messages	Count	Token	5
Data	GB	Token	10

To use tokens with a usage-based rate card, you're essentially creating a two-step currency conversion process for your products. First, customers buy virtual currency (tokens), and then they use those tokens to pay for their usage of a product or service. In this model, your rate card has two types of entries: one for the tokens themselves and another for each resource you offer.

RESOURCE	CONSUMPTION	TOKEN RATE	FINAL TOKENS
Data	102 GB	10 tokens per GB	102 x 10 = 1020 tokens
Text Messages	5500 messages	5 tokens per message	5500 x 5 = 27500 tokens

Calculating your bill: Usage Management calculates the total number of tokens used for each resource and then converts that total into a monetary value. The total number of tokens used is 28,520. If the customer had a grant of 5,000 tokens, their final overage is 28,520 - 5,000 = 23,520 tokens. At a Product Per Point (PPP) rate of $0.75 per token, the final charge is $17,640.

SEE ALSO
Enable Rate Management
Rate Card and Rate Card Entries
Clone the Default Rating Discovery Procedure
View Rate Cards for Usage-Based Assets
