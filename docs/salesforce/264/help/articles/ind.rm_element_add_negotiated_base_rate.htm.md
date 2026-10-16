---
article_id: ind.rm_element_add_negotiated_base_rate.htm
title: Add the Negotiated Base Rate Element
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_add_negotiated_base_rate.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_element_negotiated_base_rate.htm
fetched_at: 2026-09-07
---

# Add the Negotiated Base Rate Element

Here’s how you can add the Negotiated Base Rate element to your rating procedure.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
USER PERMISSIONS
NEEDED
To create, update, and delete rating procedures:	Rate Management Design Time User
From the App Launcher, find and select Rating Procedures.
To open the rating procedure record, click the procedure name.
To open the rating procedure in the Rating Procedure builder, click the rating procedure version.
Define the Rating Setting element. See Rating Element.
NOTE To access and view asset-based lookup tables, make sure Transaction Management is enabled. Alternatively, create and use custom lookup tables.
Click , and then find and select the Negotiated Base Rate element from the list.
In the Lookup Table Details field, search for and select the Asset Rate lookup table.
Map your variables to the appropriate context tags.
Click , and enter 1 as the rank number.
Click , select Include in Output, and save your rating procedure.
Click Simulate.
On the Input tab, enter the variables to simulate and verify your calculations,
Enter variable values either in JSON format (Advanced) or in the fields (Simplified).
Click Simulate and verify that the calculations are per your rating settings.
The Waterfall View shows every step of the rating calculation.
When you’re happy with the simulation result, click Activate.
EXAMPLE Sample JSON input values:
{
  "UsageRatableSummary": [
    {
      "ProductSellingModel": "",
      "UsageRatableSummaryId": "1Guxx0000004CIiCAM",
      "TierRateCardEntry": "",
      "OverageQuantity": "1",
      "UsageResource": "1BRDU0000000UjC4AU",
      "NetUnitRateUom": "0hEDU0000000UlK2AU",
      "Asset": "02iDU0000005hosYAA",
      "RatingDecisionDateTime": "2024-12-19T00:00:00.000Z",
      "TierRateCard": "",
      "IsTierNegotiated": "",
      "BaseRateCard": "",
      "SellableProduct": ""
    }
  ]
}
