---
article_id: ind.pricing_understand_your_resolution_variables.htm
title: Understand Your Resolution Variables
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_understand_your_resolution_variables.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Understand Your Resolution Variables

When you enable output resolution in your pricing element, you’ll see a new Resolution Variables section that will consume the details of the resolution strategy you’ve created. The variables in the Resolution Variables section must be mapped to accurate context tags.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
ELEMENTS	RESOLUTION VARIABLE	DESCRIPTION


List Price

Price Tracking

Price Adjustment Matrix

	Resolution Strategy	Specifies the pricing resolution strategy you’ve previously defined and saved as a procedure output resolution record. If you've not created a resolution strategy, see Configure Pricing Resolution Strategies.


List Price

Price Tracking

Price Adjustment Matrix

	Use As List	

Specifies the input variable that the pricing engine uses to determine the resolution for identifying the best price.

For example, if your input variable is a price book, the pricing engine finds the relevant value in the decision table and calculates the best price from the list of available price books.




List Price

Price Tracking

	Candidate Priority	If there is a tie in the available list of prices, then you can assign a priority to determine which one is selected.


List Price

Price Tracking

	Final Price Sequence	The final tiebreaker for determining a line item's price when a priority-based resolution strategy results in a tie. The Final Price Sequence typically selects the lowest price.

You can also use the Write Back section to store the final result of the output resolution process directly into a tag.
