---
article_id: ind.qocal_token_support.htm
title: Anchor Product with Token Commitments
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_token_support.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Anchor Product with Token Commitments

A token acts as a virtual currency, such as Flex credits or Salesforce credits. In the token-commitment model, your user purchases a quantity of tokens that has a standard conversion rate to a dollar for each service, such as SMS and data.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

For tokens, these terms help define the conversion rate.

Points Per Unit (PPU)—the anchor product defines how many tokens each specific service costs. For example, one SMS message equals five tokens, and 1 GB of data equals 10 tokens.
Price Per Point (PPP)—the quote defines the monetary cost of a single token, such as $0.75 per token.

When a sales rep creates a quote and adds a product or service, the resources are listed with their PPU. The system calculates the final price based on the number of tokens purchased multiplied by the PPP.

When consumption occurs, the rating engine converts the consumption, such as one SMS message, into tokens (five tokens). It then calculates the financial impact based on the token price.

Token-to-Cost Calculation for Usage Resources

The consumption of usage resources is calculated based on defined conversion rates. To calculate costs, Salesforce converts usage into a monetary value:

Consumption-to-Token Conversion—the consumption of a resource is converted into tokens based on a defined rate. For example, 1 GB of data storage = 2 tokens.
Token-to-Currency Conversion—the total number of tokens is converted into a monetary value by using the token's rate. For example: 1 token = US$0.20.
EXAMPLE To calculate the cost of cloud storage that uses an anchor rate:

Consider ACME, a cloud storage company that uses a token-based model. You purchase a product that provides 50 GB of storage data.

Total amount calculation:

QUANTITY	RATE	CALCULATION
50 GB	2 Cloud credits per GB	50 GB x 2 Cloud Credits per GB = 100 Cloud Credits
100 Cloud Credits	$0.20 per Cloud Credit	100 Cloud Credits x $0.20 per Cloud Credit = $20.00

The amount due for 50 GB of data is $20.00.

Token Calculation for Commitments

When token resources are linked to commitments, the calculation depends on the commitment policy. Commitment discounts apply only if the policy uses the lowest commitment rate.

EXAMPLE Consider a service that uses the anchor product Storage Plan for its base rate. For the anchor product, the unit-to-token rate is 10 and the token-to-currency rate is $0.50. The anchor product is linked to commitment product Storage-Per-Month, which provides a 20% PPU discount. The PPP rate for the commitment product is $0.30.

If you have a usage of 1,000 storage units, here's how the cost of the service is calculated by using a commitment discount.

QUANTITY	RATE	CALCULATION
1000 units	8 Revenue Events per unit (20% discount applied)	1000 x 8 = 8000 Revenue Events
8000 Revenue Events	$0.30 per Revenue Event	8000 x $0.30 = $2,400.00
The final charge for 1000 units is $2,400.00.

The final overage calculation depends on the commitment policy:

Lowest Commitment Rate: Uses the commitment rate for overage calculations, and commitment discounts apply.
Bounded Object Rate: Uses the anchor rate for overage calculations, and commitment discounts don't apply.
SEE ALSO
Create a Usage Resource
Create a Unit of Measure Class
