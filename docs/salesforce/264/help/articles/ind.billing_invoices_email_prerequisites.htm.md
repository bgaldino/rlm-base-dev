---
article_id: ind.billing_invoices_email_prerequisites.htm
title: Define Invoice Email Delivery Configuration and Preferences
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoices_email_prerequisites.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_pdf_document_delivery_through_email.htm
fetched_at: 2026-09-04
---

# Define Invoice Email Delivery Configuration and Preferences

Before you send invoices to your customers through email, your Billing admin and Billing Operations user must complete certain tasks.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Configure Email Delivery of Invoices

Before you send invoice emails, your Billing Admin must configure these settings in your Salesforce org.

If you want to send invoice emails from Invoice records, turn on Document Generation for Billing.

See Turn On Invoice PDF Document Generation and Account Statement.

If you want to send invoice emails from Invoice Batch Run records, turning on Document Generation for Billing is optional.

Turn on Configure Email Delivery Settings and select a default email template. Optionally, create custom email templates and select one as the default template instead.
See Turn On Email Delivery of Invoices, Invoice Email Prerequisites, and Create Email Templates.
Define the email preferences on Legal Entity records.
See Create Legal Entities in Revenue Management.
Enable Customer User for a Bill to Contact record to provide access to Experience Cloud sites.

See Create Experience Cloud Site Users.

A maximum of 5000 emails can be sent to the email address on Bill to Contact records daily. To send emails beyond the daily limit, enable customer user for the Bill to Contact record. Emails sent to customer community users are not counted against the 5000 daily email limit. The system first checks for a customer community user before considering the email address on the Bill to Contact record.

Enable Email Tracking to track emails in activity timeline.
See Enable Email Tracking for All Customers Opening Email from Your Company.
Define Invoice Email Delivery Preferences

Before you send invoice emails, your Billing Operations user must define these values.

Define the email preferences on Billing Account records.
See Create Billing Profiles.
Specify the email address on Bill To Contact records of invoices.
See Contact Fields.
If yours customers choose to not receive emails, edit the Contact record to opt out of receiving emails.

See Opting Out of Email.

Only the contacts that have self-service access to the Experience Cloud site can opt themselves out of receiving emails.

After you define these values, send invoice emails from Invoice records or Invoice Batch Run records.
