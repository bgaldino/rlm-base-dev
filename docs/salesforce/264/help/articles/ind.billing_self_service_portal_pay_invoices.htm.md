---
article_id: ind.billing_self_service_portal_pay_invoices.htm
title: Pay Invoices with the Self-Service Billing Portal
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_self_service_portal_pay_invoices.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_self_service_portal.htm
fetched_at: 2026-11-23
---

# Pay Invoices with the Self-Service Billing Portal

Set up the Self-Service Billing Portal so that your customers can view invoices, download invoice PDF documents, pay outstanding balances, and manage their saved payment methods. If your site uses Aura templates, add the Saved Payment Methods for Aura component to the site.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To create and configure an Experience Cloud site by using the Self-Service Billing Portal template:	Billing Admin permission set
To access the Experience Cloud site created by using the Self-Service Billing Portal template:	Billing Experience Cloud User permission set
To generate invoice PDF documents from the self-service billing portal:	DocGen Runtime Community User permission set

Before you begin, configure your Experience Cloud site users and provide them with access to view invoices and generate invoice PDF documents.

Create Customer Community Plus users or Partner Community users for your Experience Cloud site. See Experience Cloud Sites and Users in Your Salesforce Org.
Create a Sharing Set for Experience Cloud Site Users to provide your Customer Community Plus users or Partner Community users with access to view the invoice records.
Create an Experience Cloud site by using the Self-Service Billing Portal template. To meet your company’s requirements and branding, configure the site by using the Experience Cloud builder.
Assign the DocGen Runtime Community User permission set to your Customer Community Plus users or Partner Community users so the users can generate invoice PDF documents from the self-service billing portal.
Add a public group of your Customer Community Plus or Partner Community users to the DocGen Document Template Library to provide users with access to the invoice document templates. When a customer downloads an invoice without an invoice PDF document, the portal generates the document on demand. The portal uses the templates in the library to generate the invoice PDF document.

To process payments in an Experience Cloud site, specify a merchant account ID. Before you specify a merchant account ID, set up a payment merchant account.

Set Up the Self-Service Billing Portal for Payments

Configure your Experience Cloud site to accept payments by specifying merchant account details and payment method options.

On the template’s home page, from the Experiences menu, select Invoice and Payment Details.
Click the Invoice Payment Options component.
Enter a merchant account ID.
Optionally, to enable additional payment methods such as digital wallets and buy now or pay later options, enter the Payment Method Set ID. To retrieve the Payment Method Set ID, run this query in the Developer Console: SELECT Id, DeveloperName, MerchantAccountId FROM MerchAccPaymentMethodSet
Without a Payment Method Set ID, the portal shows only credit card, ACH, and saved payment methods.
Optionally, to support express payment methods such as Apple Pay, Amazon Pay, and Google Pay, add the Express Payments component to the Invoice and Payment Details page.
In the component properties, set Account ID to {!CurrentUser.effectiveAccountId}, Merchant Account to your merchant account ID, and Payment Method Set ID to your payment method set ID.
On the Invoice Payment Status page, set the Payment Method field to {!paymentMethod}.
Publish the site for the changes to take effect.

After you set up your Experience Cloud site, configure the email that you want to send to your customers. When an invoice is generated, the customer receives an email with a link to the Experience Cloud site and the details of the invoice. See Send Invoices Through Email.

Pay Invoices in the Self-Service Billing Portal

Customers can review invoice details, download invoice documents, and submit payments through the portal.

NOTE

To generate invoice PDF documents from the portal, add a public group of your portal users to the DocGen Document Template Library. See Create Public Groups and Manage Library Membership from Files Home.

On the Home tab, click the invoice number to view the invoice details.
Review the invoice lines.
To download the invoice PDF document, click Download.
Click Pay.
Verify the billing information and invoice summary.
Select the payment method, and click Pay Now.
If your customers add a payment method, they can save it for future use and set it as their default.

When the payment is processed, a notification appears with the payment status. If the payment is successful, the invoice is marked as settled. If any invoice is locked, your customers can contact your admin for help.

Add Saved Payment Methods Component to an Aura Experience Cloud Site

With the Saved Payment Method for Aura component, your customers can view, add, delete, and set a default payment method from your site.

In Experience Builder (Aura), open the page where you want to add the component.
In the components list, find Saved Payment Methods for Aura, and drag it onto your page.
Enter a Merchant Account Id.
Publish your site for the changes to take effect.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_self_service_portal_pay_invoices.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
