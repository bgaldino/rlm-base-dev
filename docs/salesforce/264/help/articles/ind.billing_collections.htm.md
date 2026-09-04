---
article_id: ind.billing_collections.htm
title: Manage Collections for Accounts in Billing
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_collections.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing.htm
fetched_at: 2026-09-04
---

# Manage Collections for Accounts in Billing

To recover overdue invoices, your collections reps use Collections workflow to track payments, record customer payment promises, and send personalized, automated dunning emails to minimize bad debt and maintain healthy cash flow.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Key Terms

Collection Plan: A record that a collections rep uses to manage an account’s overdue invoices. It shows the account’s total invoice balance, due date, contact details, usage type, collection plan segment, timeline, collection plan items, and payment promises.

Collection Plan Item: An individual invoice on a collection plan. A collection plan can include multiple collection plan items, each corresponding to a different invoice for the same account.

Process Workflow

The Collections feature provides collections reps a structured process for recovering invoice balances.

A collections rep creates a collection plan to track and resolve an account's unpaid or partially paid invoices, then adds each invoice as a collection plan item.

A collections rep initiates dunning orchestration for a collection plan. Billing uses predefined Dynamic Revenue Orchestrator templates to send a milestone-driven sequence of reminders and escalations based on the collection plan’s due date and collection plan segment. Low- and medium-risk accounts receive an early reminder, a due notice, and a suspension notice before the process escalates to manual recovery. The dunning process starts earlier and escalates faster for high-risk accounts. Billing triggers each email or task on the specified date or after the specified day offset, so the dunning process continues until it reaches a manual action, such as a recovery call.

The collections rep then makes recovery calls to customers and records their payment commitments as payment promises. The collections rep generates a payment schedule and payment schedule items with one payment or up to 3 partial payments, each with a due date and amount. A payment batch run then processes these payment schedule items and applies the successful payments to the invoice.

The collections rep can track all recovery activity for an account from the collection plan and its collection plan items. If an invoice is deemed uncollectible, a collections rep can write it off.

Business Use Case: Managing Collections for an Overdue Invoice

Acme Software Innovations provides a cloud-based analytics platform to its customer, Growth Digital Marketing Pro, through a monthly subscription. Growth Digital Marketing Pro owes Acme Software Innovations US$60,600 for an invoice due on March 31, 2025.

Acme Software Innovations’ collections rep reviews the invoice and finds that Billing classified it as high risk and initiated the orchestrated dunning process. Growth Digital Marketing Pro hasn’t paid the invoice or responded to the email reminders.

The collections rep contacts Growth Digital Marketing Pro to negotiate repayment. Growth Digital Marketing Pro agrees to pay in two equal installments. The collections rep creates these payment promises for the collection plan and uses Growth Digital Marketing Pro’s preferred saved payment method.

Payment Schedule: PS0000006

Payment Schedule Item 1: PSI0000001, $30,300 due on May 31, 2025
Payment Schedule Item 2: PSI0000002, $30,300 due on June 30, 2025

The collections rep then schedules a few follow-up reminders based on the new payment schedule due date.

Key Features
Collections App: Create, view, and monitor collection plans and collection plan items for accounts with overdue invoices to manage the invoice recovery process.
Dunning Emails: Leverage out-of-the-box email capabilities of Salesforce to set up and send personalized email reminders to notify customers about overdue invoice balance or upcoming payments. Use Dynamic Revenue Orchestrator templates to orchestrate your dunning strategy for collections. You can use the email templates that are available as part of the dunning orchestration solution to send automated email reminders for your collection plans. However, if you have Marketing Cloud, you can also design dunning campaigns and tailor your email communication for specific customer segments.
Timeline: Track the timeline of unpaid invoices from collections initiation and email communications to scheduled calls. You can also view upcoming tasks such as calling the customer or sending a second email reminder by using the New Task  icon on the activity panel in your collections timeline. See Enable Timeline for Collections and Set Up a Timeline in Salesforce.
Payment Promises: Communicate with the customers, receive payment commitments, and set up payment schedules to streamline the payment process.
Create Collection Plans and Collection Plan Items
Create collection plans for accounts to help your collections reps track and resolve unpaid invoices. Create collection plan items for unpaid invoices that are related to the collection plan's account, enabling your collections rep to focus on the payment collection for individual invoices.
Orchestrate Your Dunning Strategy for Collections
Automate the entire dunning journey—from sending email reminders to manual recovery on payment collections—by using the out-of-the-box Dynamic Revenue Orchestrator (DRO) templates.
Collect Payment Promises for a Collection Plan Item
Record your customer's payment promises, and create payment schedules and payment schedule items for collection plan items. Collections reps can secure payments for the outstanding balance of the invoice related to the collection plan item.
Set Up and Send Dunning Emails
Configure automated dunning campaign emails to improve overdue invoice collections. Your collections reps can schedule timely overdue payment email reminders on a recurring basis, helping improve payment recovery rate and reduce collections efforts.
Collections Specialist Console
Use the Collections Specialist Console to manage your day to day collections from a single screen. Track receivables, invoice aging, and payment promises, and take necessary action directly from the console.
