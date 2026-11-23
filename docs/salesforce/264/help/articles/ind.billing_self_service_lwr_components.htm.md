---
article_id: ind.billing_self_service_lwr_components.htm
title: Add Billing Components to LWR Experience Cloud Sites
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_self_service_lwr_components.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_self_service_portal.htm
fetched_at: 2026-11-23
---

# Add Billing Components to LWR Experience Cloud Sites

Add billing self-service capabilities to any Experience Cloud site that uses Lightning Web Runtime (LWR) templates, including a site that you build yourself. Drag the Posted Invoices, Invoice Line Viewer, Invoice Payment Options, Self-Service Payment Confirmation, and Saved Payment Methods components onto your pages so that customers can view invoices, pay outstanding balances, and manage their saved payment methods from your own branded site.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To use the Billing self-service components in an Experience Cloud site:	Billing Experience Cloud User permission set

The Self-Service Billing Portal template gives you a ready-to-use site. These components add the same billing capabilities to any LWR site, including the Build Your Own (LWR) template.

These components are available in the components palette, under the Layout section, in Experience Builder.

Posted Invoices: Shows a list of posted invoices for the current user's account.
Invoice Line Viewer: Shows the line items of an invoice.
Invoice Payment Options: Shows the payment methods available for an invoice, including saved payment methods. Customers can also add a new payment method, save it for future use, and then submit a payment.
Self-Service Payment Confirmation: Shows whether a payment submitted from the Invoice Payment Options succeeded.
Saved Payment Methods: Shows customers their saved payment methods and provides options to add or delete a saved payment method and set a default."
Add a Billing Component to Your Page
In Experience Builder, open the page where you want to add the component.
In the components palette, under Layout, find the component that you want to add.
Drag the component onto your page.
Configure the component's properties.

Required fields vary by component.

NOTE Some components need redirect links to other components. For example, Invoice Payment Options redirects to the site page for payment confirmation.
Publish your site for the changes to take effect.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_self_service_lwr_components.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
