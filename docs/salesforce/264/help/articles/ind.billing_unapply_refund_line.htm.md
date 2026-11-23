---
article_id: ind.billing_unapply_refund_line.htm
title: Unapply a Refund Line Payment
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_unapply_refund_line.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_refunds_overview.htm
fetched_at: 2026-11-23
---

# Unapply a Refund Line Payment

Unapply a refund line payment applied to the wrong payment or for the wrong amount, and then restore the refund and payment balances. To unapply, create a refund line payment of type Unapplied that's linked to the original application.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS
NEEDED
To unapply a refund line payment:	

Payment Admin permission set

Or

Payment Operations User permission set

An unapply always reverses the full amount of the original application. You can unapply each applied refund line payment only one time.

On the refund, click the Related tab.
In the Refund Line Payments related list, find the refund line payment that you want to reverse. Make sure that its Type is Applied and Has Been Unapplied is No.
In the Refund Line Payments related list, click New.
The Refund field populates automatically.
For Type, select Unapplied.
For Associated Refund Line Payment, select the refund line payment that you want to reverse.
For Has Been Unapplied, select NA.
(Optional) For Unapplied Date, enter a date on or after the Applied Date of the associated refund line payment.
If you leave it blank, Billing uses the current date and time.
Set the Amount, Refund, Payment, and Currency ISO Code fields to the same values as the associated refund line payment.
If you leave Applied Date or Associated Account blank, Billing copies the value from the associated refund line payment.
Save the changes.
EXAMPLE

A $100 refund is applied through two refund line payments of $60 and $40. The $40 application is incorrect, so you unapply it. Billing changes the refund's Balance from $0 to $40, Total Unapplied from $0 to $40, and Net Applied from $100 to $60. You can then apply the $40 to the correct payment.

To confirm the unapply, check the refund, the payment, and the original refund line payment. On the refund, Balance and Total Unapplied increase by the unapplied amount, and Net Applied decreases by the same amount. On the payment, Balance increases by the same amount. On the original refund line payment, Has Been Unapplied is Yes and Unapplied Date is filled in.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_unapply_refund_line.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
