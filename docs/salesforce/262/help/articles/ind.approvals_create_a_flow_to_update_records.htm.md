---
article_id: ind.approvals_create_a_flow_to_update_records.htm
title: User Interface, Component, and List View Behavior
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_create_a_flow_to_update_records.htm&type=5&release=262
release: 262
release_name: Summer '26
area: approvals
fetched_at: 2026-05-12
---

# User Interface, Component, and List View Behavior

This section covers known behaviors and limitations for front-end components and list views.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions where Advanced Approvals is enabled
Approval Trace Component

The Approval Trace component is a predefined, locked tool that you can’t customize.

The component shows only the record that’s associated with the approval submission. It doesn’t show details for its related records. For example, if you submit an approval for a quote line item, the Approval Trace component doesn’t show the work items associated with the parent quote. If your business requires extended visibility from a single page, redesign the approval flow.

Approval List Views
You can’t modify the filters in the Assigned Approval Work Items list view.
Custom list views cannot filter approval work items by ownership because the Approval Work Item object lacks an Owner field. To view the work items assigned to you, use the Assigned Approval Work Items list view.
You can't modify the sharing settings of the default list views in Advanced Approvals.
You can't delete any default list view in Advanced Approvals.
Approval Object Page Layout Customization

You can't customize the layout of the Approval object pages before the records are created.

To override the default page layout for objects, you can do the following.

Viewing a record after creation activates the default page layout.
From the App Launcher, search for any Approval object. Change the view to a List View, then click on any record. When you click the Details tab, the object's page layout is activated.
