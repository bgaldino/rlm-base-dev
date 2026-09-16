---
article_id: ind.billing_self_service_lwr_components.htm
title: Add Billing Components to LWR Experience Cloud Sites
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_self_service_lwr_components.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_self_service_portal.htm
fetched_at: 2026-09-04
---

# Add Billing Components to LWR Experience Cloud Sites

Add billing self-service capabilities to any Experience Cloud site that uses Lightning Web Runtime (LWR) templates, including a site that you build yourself. Drag the Posted Invoices, Invoice Line Viewer, Self-Service Payment Sheet, Self-Service Payment Confirmation, and Manage Saved Payment Methods components onto your pages so that customers can view invoices, pay outstanding balances, and manage their saved payment methods from your own branded site.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To use the Billing self-service components in an Experience Cloud site:	Billing Experience Cloud User permission set

The Self-Service Billing Portal template gives you a ready-to-use site. These components add the same billing capabilities to any LWR site, including the Build Your Own (LWR) template.

These components are available in the components palette, under the Layout section, in Experience Builder.

Posted Invoices: shows a list of posted invoices for the current user's account.
Invoice Line Viewer: shows the line items of an invoice.
Self-Service Payment Sheet: shows the payment methods available for an invoice, including saved payment methods. Customers can also add a new payment method, save it for future use, and then submit a payment.
Self-Service Payment Confirmation: shows whether a payment that a customer submitted from the Self-Service Payment Sheet succeeded.
Manage Saved Payment Methods: shows customers their saved payment methods so that they can add or delete a saved payment method and set a default.
Add a Billing Component to Your Page
In Experience Builder, open the page where you want to add the component.
In the components palette, under Layout, find the component that you want to add.
Drag the component onto your page.
Configure the component's properties.

Required fields vary by component.

NOTE

Some components need redirect links to other components. For example, Self-Service Payment Sheet redirects to the site page for payment confirmation.

Publish your site for the changes to take effect.
