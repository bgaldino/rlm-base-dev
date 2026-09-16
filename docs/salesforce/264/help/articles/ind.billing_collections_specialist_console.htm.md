---
article_id: ind.billing_collections_specialist_console.htm
title: Collections Specialist Console
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_collections_specialist_console.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_collections.htm
fetched_at: 2026-09-04
---

# Collections Specialist Console

Use the Collections Specialist Console to manage your day to day collections from a single screen. Track receivables, invoice aging, and payment promises, and take necessary action directly from the console.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.

From the App Launcher, find and select Collections. From the navigation bar, click Collections Specialist Console.

If you don't see the console, ask your Salesforce admin to complete the setup first. See Set Up the Collections Specialist Console.

Filters

Use the Account and Currency filters to keep your whole team working from the same prioritized view, whether you're focused on one account or comparing several. To remove a filter, select All Accounts or All Currencies. If your Salesforce org has multiple currencies enabled, select a specific currency to see totals in the cards and charts.

Summary

Four cards show your overall receivables position at a glance.

Outstanding Receivables: Total unpaid, posted invoice balance, with the invoice count.
Current Due: Unpaid invoices due today or in the future.
Overdue: Unpaid invoices that are past due.
Unapplied Payments: Payments with available balance.

Outstanding Balance totals unpaid invoices and debit memos for the selected account, minus unapplied credits and unapplied payments.

Collection Progress

Use the donut chart to compare your Recovered balance against your Outstanding balance for the selected account and currency. The chart shows the total amount you still need to recover, compared with how much you've already recovered. The chart records the total invoice balance from the collection plan item at the time of creation. View each balance's amount in the legend below the chart.

My Tasks

Review your open tasks linked to a collection plan. The console sorts these by due date to show what's due next.

My Collection Plans

Track your collection plans within the console. Use the sidebar card to see Open and Closed plan counts and access their details. The table below the tabs lists each plan's ID, due date, and account. Use the Create Collection Plan button to start a plan that isn't tied to a specific invoice selection.

Invoice Aging and Payment Promises Charts

Switch between two charts to identify outstanding balance concentrations and expected payments.

View your unpaid invoice total across five overdue-day buckets (Current Due, 30 Days Overdue, 31 to 60 Days Overdue, 61 to 90 Days Overdue, and More Than 90 Days Overdue) in the Invoice Aging bar. Click a bucket to open a filtered list view of the underlying invoices.

Group payment schedule items by status (Ready for Processing, Draft, Failed, and Processing) in the Payment Promises chart. Click a status to open a filtered list view.

Invoice and Dispute Tabs

Act on invoices and disputes using the three tabs. Each tab provides a list-view picker, a table of records, and an Open List View link. Scroll to load more rows automatically.

TAB	SHOWS	AVAILABLE ACTIONS
Critical Follow-Ups	Posted invoices with a balance greater than 0, more than 30 days overdue	Create Collection Plan, Write Off Invoice, Create Task
High-Value Overdue Invoices	Posted invoices with a balance greater than $2,000	Send Reminder, Create Task, Create Collection Plan
Invoice Disputes	Open disputes on invoices, shown as dispute records rather than invoice records	Send Reminder, Resolve Case, Create Task

Switch among prebuilt and custom views using each tab's list-view picker. Use the Open List View option to create a new view, edit an existing view's filters, or rename a view. It opens the list view page for that tab's records with your current view applied, so you can create, edit, and rename list views there. A renamed view keeps its new name on the console.

To act on a row, select one or more records in a tab, and then click an action button.

ACTION	DESCRIPTION
Create Collection Plan	Select one or more invoices, then click Create Collection Plan to create a plan covering them. The button is unavailable if a selected invoice already has a linked collection plan. To create a plan without selecting invoices, use Create Collection Plan in My Collection Plans instead, or see Create Collection Plans and Collection Plan Items to build one field at a time.
Write Off Invoice	Select a single invoice, then click Write Off Invoice to open the dialog. Select a value from the Reason Code picklist and, optionally, enter a Description, then save your changes. Refresh the page after some time to see the invoice removed from the tab and the balance updated. Behind the scenes, the system creates and applies a credit memo for the amount you're writing off. To understand how write-offs and credit memos work, see Write Off Invoices.
Send Reminder	Select an invoice, then click Send Reminder to send a payment reminder to the invoice's billing contact through Salesforce's standard Send Email action.
Resolve Case	Select a single dispute, then click Resolve Case to open the case record linked to it. From there, click the case's own Resolve Case action, select the resolution type that matches the request, and finish. Billing completes the resolution and closes the case. For the full workflow by request type, see Resolve Billing Service Requests.
Create Task	Select a single invoice or dispute, then click Create Task to open the task composer and log a follow-up task.
Set Up the Collections Specialist Console
Grant your collections team access to the Collections Specialist Console: turn on the tab and add the console to the Collections app.
