---
article_id: ind.qocal_sell_commitment_based_usage_products.htm
title: Sell Commitment-Based Usage Products
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_sell_commitment_based_usage_products.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Sell Commitment-Based Usage Products

For selling commitment-based usage products, a sales rep must follow a three-step process—creating the anchor product, creating the commitment product, and linking the anchor and commitment products together.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create quotes:	Create on Quotes

Let’s take a scenario where a customer wants to purchase Quantum Bit Database—the anchor product, and wants to commit to 1,000 tokens to secure a discounted rate.

SEE ALSO
Build a Quote for Usage-Based Products
Anchor Product with Token Commitments
Create a Usage Commitment Asset Related Object
Step 1: Quote and Assetize the Anchor Product

The anchor product represents the primary service that tracks the customer's consumption.

Create a quote and add the Anchor product—Quantum Bit Database Token Offering.
Under Quote Line Items, from the quick actions, click Manage Usage Resources.
On the Manage Usage Resource page, the Usage Resources table shows the resources included in the product, for example, DB Storage, Compute Time. The table also shows the default token values for each resource, such as 10 tokens per GB.
Save the quote.
Generate the order, and activate it. The activation process creates an asset for the anchor product.
Step 2: Quote and Assetize the Commitment Product

The Commitment product defines the minimum usage or spends and the discounted pricing.

Create a quote and add a commitment product from the catalog—Quantum Token Commitment.
Enter the commitment parameters. For example, the customer commits to 1,000 units of Quantum Tokens.
For the commitment of 1000 tokens, a 6% discounted rate and an extra grant of 10 GB of storage and 10 minutes of compute time are provided.
Save the quote.
Generate the order, and activate it. The activation process creates an asset for the commitment product.
Step 3: Link the Commitment to the Anchor Assets

To apply discounts available in the commitment product to the consumption of the anchor product resources, the two standalone assets must be tied together by using a junction object Usage Commitment Asset Related Object.

NOTE You can’t link multiple commitment products to the same anchor that have the same validity period.
From the App Launcher, find and select Usage Commitment Asset Related Objects.
Click New.
In the Related Object field, select Asset and then select the anchor product you assetized in Step 1 (Quantum Bit Database).
In the Asset field, select the commitment product you assetized in Step 2 (Quantum Token Commitment).
Select an effective start and end date.
Save your changes.

The commitment product is now configured. Whenever the customer consumes DB Storage or Compute Time against their Anchor product, the rating engine processes the consumption by using the 6% discounted rate provided by the linked Commitment.
