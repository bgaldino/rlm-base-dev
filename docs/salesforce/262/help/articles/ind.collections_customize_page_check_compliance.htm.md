---
article_id: ind.collections_customize_page_check_compliance.htm
title: Customize Lightning Pages to View Compliance Check Information
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_customize_page_check_compliance.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_compliance_setup.htm
fetched_at: 2026-08-04
---

# Customize Lightning Pages to View Compliance Check Information

To show the outbound call compliance details for the borrowers associated with the collection plan, add the CallComplianceDetailsForBorrowers component to the collection plan record page.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To customize a Lightning record page:	

Collections and Recovery Admin permission set

AND

Modify All Data permission

AND

Customize Application permission

AND

OmniStudio Admin permission set

AND

FSC Sales permission set

The CallComplianceDetailsForBorrowers component shows a list of all borrowers with phone numbers and enables collection specialists to check the call compliance for each borrower. The component also shows the status of call compliance.

From the App Launcher, find and select Collections.
Click Collection Plans, and open a collection plan record details page.
Click , and then select Edit Page.
Drag the Flexcard component from the Components panel to the Lightning page canvas location where you want to position the component on the record page.
In the Properties pane, select the CallComplianceDetailsForBorrowers Flexcard.
Save your changes.
