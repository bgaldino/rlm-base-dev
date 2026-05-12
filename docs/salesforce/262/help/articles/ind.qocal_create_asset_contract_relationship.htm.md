---
article_id: ind.qocal_create_asset_contract_relationship.htm
title: Create Asset Contract Relationships
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_asset_contract_relationship.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Create Asset Contract Relationships

Manually link assets to a contract to track which products-specific customer agreements govern. Creating these relationships helps you to review contract details or open related contracts directly from an asset record.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS
NEEDED
To create an asset contract relationship:	Sales Operations Rep permission set
 	 
IMPORTANT Verify that the asset and the contract belong to the same account. Make sure that your Salesforce admin has added the Asset Contract Relationship component to your Asset and Contract page layouts.

If an order is linked to a contract with a Agentforce Revenue Management application usage assignment, the system automatically creates asset contract relationships. This automation occurs when the Create or Update Asset from Order API or Order Product API runs. These automated records default the start and end dates to match the parent asset's lifecycle dates, though the relationship end date can’t exceed the contract's end date.

In the App Launcher, find and select Assets or Contracts.
Select an asset name or contract number.
On the Related tab, locate Asset Contract Relationships, and click New.
Starting from an asset defaults to the Asset field.
Starting from a contract defaults to the Contract field.
Search for and select the corresponding asset or contract.
Select a start date and time.
End Date and Time are optional.
If the parent asset has a lifecycle end date in the past, you can't set an asset contract relationship end date in the past.
Save your changes.

After linking your assets, use the Managed Assets Viewer on the contract record to perform lifecycle actions like amending, renewing, or canceling assets.

SEE ALSO
Add a Related List to an Object
Customize Related Lists
