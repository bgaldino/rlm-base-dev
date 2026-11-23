---
article_id: ind.billing_setup_payment_schedules_and_payment_schedule_items_enable.htm
title: Automatic Creation of Payment Schedules and Payment Schedule Items
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_payment_schedules_and_payment_schedule_items_enable.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_schedules_and_payment_schedule_items_auto_manual.htm
fetched_at: 2026-11-23
---

# Automatic Creation of Payment Schedules and Payment Schedule Items

Automate the creation of payment schedules and payment schedule items so that they are ready to be processed.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Cloud
To integrate a native payment gateway, you have two options. Use Salesforce Payments, which runs on Stripe and is available with the the Revenue Cloud Billing license on a cost-per-transaction basis. Or, connect your own Adyen account, contracted directly with Adyen.
 
Process Overview

When your Payments admin enables the Create Payment Schedules and Payment Schedule Items feature for the first time, these default records are created for your Salesforce org:

DEFAULT RECORD FOR	RECORD NAME	KEY FIELD VALUES
Payment Schedule Policy	Default Payment Schedule Policy	
Payment Schedule Policy Status value: Active
Payment Schedule Treatment Selection value: Default

Payment Schedule Treatment	Default Payment Schedule Treatment	
Payment Schedule Treatment Status value: Active
Automation Trigger Source value: Invoice Posted

Payment Schedule Treatment Detail	Default Payment Schedule Treatment Detail	
Installment Payment Type value: Percentage
Percentage value: 100
Processing Date Reference value: Invoice Due Date
Payment Method Selection Type value: Most Recent Autopay

Payment Schedule Distribution Method	Default Payment Schedule Distribution Method	
Distribution Method Type value: Full Distribution
Distribution Count value: 1
Payment Schedules and Payment Schedule Items

A Payment Schedule record and a Payment Schedule Item record are created based on the configuration of these default records. So, each time an Invoice record is posted, a single Payment Schedule record is created with the entire invoice balance amount as the total requested amount. A single Payment Schedule Item record is created for each Payment Schedule record. You can also group multiple invoices of an account to generate a consolidated Payment Schedule and Payment Schedule Item record.

Access to Edit Payment Schedules and Payment Schedule Items

The user that turns on Create Payment Schedules and Payment Schedule Items is the owner of the default Payment Schedule Treatment record, and the Payment Schedule and Payment Schedule Item records that are automatically created. To enable other users to edit Payment Schedule records and Payment Schedule Item records, set the default internal access of the Payment Schedule object and Payment Schedule Item object to Public Read/Write.

SEE ALSO
Revenue Cloud Developer Guide: PaymentSchedule
Revenue Cloud Developer Guide: PaymentScheduleItem
Revenue Cloud Developer Guide: PaymentSchedulePolicy
Revenue Cloud Developer Guide: PaymentScheduleTreatment
Revenue Cloud Developer Guide: PaymentScheduleTreatmentDtl
Revenue Cloud Developer Guide: PymtSchdDistributionMethod

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_setup_payment_schedules_and_payment_schedule_items_enable.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
