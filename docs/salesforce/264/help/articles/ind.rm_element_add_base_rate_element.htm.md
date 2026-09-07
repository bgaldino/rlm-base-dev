---
article_id: ind.rm_element_add_base_rate_element.htm
title: Add the Base Rate Element
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_add_base_rate_element.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_element_base_rate.htm
fetched_at: 2026-09-07
---

# Add the Base Rate Element

Here’s how you can add the Base Rate element to your rating procedure.

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
Click , and then find and select the Base Rate element from the list.
In the Lookup Table Details field, search for and select the Rate Card Entries 2 lookup table.
Map your variables to the appropriate context tags.
Click , and enter 1 as the rank number.
NOTE When more than one enabled version matches a rating procedure, choose the version with the highest rank. For example, if two enabled versions have rank values set to 1 and 2, choose the version with rank 2.
Click , select Include in Output, and save your rating procedure.
Click Simulate.
On the Input tab, enter variable values.
You can enter the values either in JSON format (Advanced) or in the fields (Simplified).
In the Input tab, click Simulate.
Verify that the calculations are as per your rating settings.
The Waterfall View shows every step of the rating calculation.
When you’re happy with the simulation result, click Activate.
EXAMPLE Sample JSON input values:
{
  "UsageRatableSummary": [
    {
      "RatingDecisionDateTime": "2024-08-07T12:59:47.403Z",
      "OverageQuantity": "5",
      "NetUnitRateUom": "0hEDU00000000Vf2AI",
      "ProductSellingModel": "",
      "UsageResource": "1BRDU00000000UP4AY",
      "SellableProduct": "",
      "BaseRateCard": "1CIDU00000000SJ4AY",
      "UsageRatableSummaryId": "1GuDU00000000My4AI"
    }
  ]
}
