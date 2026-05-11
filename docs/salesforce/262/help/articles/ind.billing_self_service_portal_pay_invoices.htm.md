---
article_id: ind.billing_self_service_portal_pay_invoices.htm
title: Pay Invoices with the Self-Service Billing Portal
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_self_service_portal_pay_invoices.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Pay Invoices with the Self-Service Billing Portal

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Pay Invoices with the Self-Service Billing Portal

When your customers log in to the self-service billing portal, they can view invoices, download invoice PDF documents, and pay outstanding balances for the invoices. The Home tab shows the list of invoices that aren't settled, partially settled, and settled.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To create and customize an Experience Cloud site by using the Self-Service Billing Portal template:	Billing Admin permission set
To access the Experience Cloud site created by using the Self-Service Billing Portal template:	Billing Experience Cloud User permission set

Before you begin, configure your Experience Cloud site users and provide them access to view invoices.

Create Customer Community Plus users or Partner Community users for your Experience Cloud site. See Experience Cloud Sites and Users in Your Salesforce Org.
Create a Sharing Set for Experience Cloud Site Users. to provide your Customer Community Plus users or Partner Community users with access to view the invoice records.
Create an Experience Cloud site by using the Self-Service Billing Portal template. To meet your company's requirements and branding, customize the site with the Experience Cloud builder.
To process payments in an Experience Cloud site, specify a merchant account ID.

Before you specify a merchant account ID, set up a payment merchant account.

On the template’s home page, from the Experiences menu, select Invoice and Payment Details.
Click Invoice Payment Options component.
Enter a merchant account ID.
After you set up your Experience Cloud site, configure the email that you want to send to your customers. When an invoice is generated, the customer receives an email with a link to the Experience Cloud site and the details of the invoice. See Send Invoices Through Email.
To view the details of an invoice, click the invoice number on the Home tab.
To pay for an invoice immediately, click Pay.
Review the invoice lines.
To download the invoice PDF document, click Download.
To pay the invoice amount, click Pay.
Verify the billing information and invoice summary.
Select the payment method, and click Pay Now.
If your customers add a payment method, they can save it for future use and set it as their default.

When the payment is processed, a notification appears with the payment status. If the payment is successful, the invoice is marked as settled. If any invoice is locked, your customers can contact your admin for help.
