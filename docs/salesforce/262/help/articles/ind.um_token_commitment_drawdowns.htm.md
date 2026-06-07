---
article_id: ind.um_token_commitment_drawdowns.htm
title: Token Commitment Drawdowns
source_url: https://help.salesforce.com/s/articleView?id=ind.um_token_commitment_drawdowns.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Token Commitment Drawdowns

The consumption process for token commitments uses a two-step rating procedure. The process in the first step converts usage to tokens, and then in the second step, tokens to currency.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license
Step 1: PPU (Points Per Unit) - Usage to Token Conversion
Transaction journal records are aggregated to generate a usage summary for each resource within the billing period.
Consumption is drawn from the earliest expiring usage entitlement bucket associated with the anchor product, or from the grants provided by commitments.
The discount provided by the commitment is applied to the anchor's base rate to calculate the token charge for any overages.
The tokens are calculated for each resource and added to the Usage Summary.
Step 2: PPP (Price Per Point) - Token to Currency Conversion
Calculated PPU charges are aggregated across all resources to generate a row for the token resource in the usage summary.
Tokens are drawn from the earliest expiring usage entitlement bucket for tokens associated with the anchor, or from the commitments.
The token overages are rated into a real currency value, and then a liable summary is generated for invoicing. The resulting invoice shows the tokens or credit points rated in the final currency.
EXAMPLE A customer buys a Data Cloud Premium product with these configurations.
PRODUCT	RESOURCE	ANCHOR RATE	COMMIT RATE	COMMITTMENT
Data Cloud Premium	Data Credits	$5 per credit	$2.5 per credit (PPP)	1,000 credits per month
API Calls	3 credits per API Call (PPU)	3 credits per API Call (PPU)	 
Storage	5 credits per GB (PPU)	5 credits per GB (PPU)	 

The customer consumes 200 API Calls and 25 GB of storage in the first month. Here’s how the consumption is calculated.

RESOURCE	CONSUMPTION	BUCKET BALANCE	OVERAGE
API Calls	

200 API Calls

200 x 3 = 600 credits

	 	 
Storage	

25 GB

25 x 5 = 125 credits

	 	 
Data Credits	725 credits	275 credits	Nil

In the second month, consumption grew to 800 API Calls and 30-GB storage. So, here’s how the consumption is calculated.

RESOURCE	CONSUMPTION	BUCKET BALANCE	OVERAGE
API Calls	

800 API Calls

800 x 3 = 2400 credits

	 	 
Storage	

30 GB

30 x 5 = 15 credits

	 	 
Data Credits	2550 credits	1000-2550=-1550	Overage by 1550 credits

The consumption leads to an overage of 1550 credits. The commitment policy specifies that after the commitment is fulfilled the bounded targeted rates apply. Therefore, the amount that the customer is liable to pay is $7750 (1550 x $5).
