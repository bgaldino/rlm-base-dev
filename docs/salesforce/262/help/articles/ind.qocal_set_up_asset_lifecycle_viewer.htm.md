---
article_id: ind.qocal_set_up_asset_lifecycle_viewer.htm
title: Add the Managed Asset Viewer Page Layouts
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_asset_lifecycle_viewer.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Add the Managed Asset Viewer Page Layouts

To view a consolidated list of lifecycle-managed assets, add the Managed Asset Viewer to your account and contract record pages. The Managed Asset Viewer shows standalone and bundled assets. Users expand bundled assets to view the bundle hierarchy and edit data within the viewer or through a side panel.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS
NEEDED
To add the Managed Asset Viewer component to page layouts:	Customize Application
NOTE The Managed Asset Viewer component shows the assets for Agentforce Revenue Management contracts only when an application usage assignment named RevenueLifecycleManagement exists.

Users expand their asset view by selecting the asset name to turn on the side panel for more details and attributes. Users edit data within the Managed Asset Viewer or through the side panel. To go to the asset record, click View on the asset row action.

From the management settings for the Accounts or Contracts object that you want to edit, go to Page Layouts.
Create a page layout or modify an existing one.
In the Related Lists section, ensure that the Assets related list is on the page.
Edit the columns in the Assets related list by clicking the gear icon and selecting the fields to show as columns.
The Assets related list fields determine the default fields in the Managed Assets related list.
Save your changes.
Go to Lightning Record Pages, select your page layout, and click Edit to open the Lightning App Builder.
Drag the Related Lists component and the Managed Asset Viewer component on the layout.
Select the checkbox to show the side panel when a user clicks a record link.
The Assets related list and the Managed Assets related lists appear on the page. By default, the Managed Assets list shows the same columns that are shown in the Assets related list.
Configure the columns in the Managed Assets related list.
To change columns, click Select under Display Columns, select columns from the Available list, and move them to the Selected list.
The Managed Asset Viewer shows your selected columns.
Save your changes.
NOTE The Asset Viewer shows only attributes active on the current date; attributes with future start dates remain hidden until they become effective.
