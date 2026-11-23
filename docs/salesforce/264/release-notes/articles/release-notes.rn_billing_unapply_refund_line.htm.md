---
article_id: release-notes.rn_billing_unapply_refund_line.htm
title: Undo Refund Line Applications with Unapply Support
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_billing_unapply_refund_line.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_billing_payments_refunds.htm
fetched_at: 2026-11-23
---

# Undo Refund Line Applications with Unapply Support

Correct a refund application without starting over. Unapply a refund line payment to reduce the refund balance automatically and update the total unapplied amount on the refund. The original refund line payment shows that it has been unapplied.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Cloud, with the Revenue Cloud Billing license.

Who:

To unapply a refund line payment, you need the Payment Admin or the Payment Operations User permission set.

How: Create a refund line payment record. Set Type as Unapplied, and set Associated Refund Line Payment to the original refund line payment of type Applied. Set the Unapplied Date on or after the applied date. The amount, applied date, refund, payment, associated account, and currency on the unapplied refund line payment must match the associated refund line payment.

SEE ALSO
Salesforce Help: Unapply a Refund Line Payment

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=release-notes.rn_billing_unapply_refund_line.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
