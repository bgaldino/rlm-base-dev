---
article_id: release-notes.rn_billing.htm
title: Billing
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_billing.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_revenue.htm
fetched_at: 2026-09-30
---

# Billing

Billing introduces key enhancements for flexible revenue operations such as weekly billing, new-sale ramp details, billing frequency changes during amendments, alongside catch-up bill runs and billing forecasts. Accelerate cash collections and recover bad debts by using tracking and visualization tools for collections. Expand payment capabilities and enhance payment flows by using self-service digital wallets, regional payment options, Lightning Web Runtime (LWR) Experience Cloud components, payment reconciliation, and credit balance refunds. Extend the Revenue Standard Tax Engine for custom tax rules and orchestrate the entire checkout flow with the Checkout API.

Customer 360
Get clear visibility across billing, collections, and invoicing operations. A new timeline view tracks billing schedule lifecycles and milestones, while account-level invoice aging summaries display consolidated balance metrics. Additionally, the new Split Invoices tab provides cross-account visibility and automatically synchronizes posting, voiding, or deleting actions across all linked records.
Billing Schedules and Billing Arrangements
Amend billing frequencies on existing subscriptions or orders. Bill weekly or bill at custom intervals that span longer periods. Skip charges for periods that fall within a future-dated suspension, surface ramp segment identifiers on billing schedules for new-sale ramp deals, and automatically compute price uplifts on multiyear ramp deals.
Invoice Management
Invoice each account for every billing schedule group that the account owns or is billed for. Resume billing on migrated schedules without reissuing past invoices, produce invoice documents during batch runs, and embed record fields into invoice and credit memo numbering. Set invoice target dates by calendar day or number of billing periods, track each schedule's periods and milestones on a timeline, review linked split invoices before you act, and forecast upcoming charges before invoices are created.
Tax Management
Adapt tax calculations to your business needs without writing Apex code.
Payments and Refunds
Pass Level 2 and Level 3 payment data via Stripe and Adyen. Support flexible customer payment options through saved digital wallets and regional payment methods. Add Billing Self-Service components on LWR Experience Cloud sites, refund available credit balances back to the account, and automatically reconcile payment advice records with bank statements.
Collections
Improve collections with invoice aging insights and manage critical overdue accounts from a single console.
Orchestrate Cart-to-Cash Checkout Flow With a Single API Call
Complete a full purchase journey with the Checkout API, whether you initiate it from an external CPQ system, a website, or a custom sales channel. Simplify integration by using a single API request to create a subscription, generate an invoice, and process and apply the payment, instead of multiple calls.
New and Changed Objects for Billing
Store and access more data with these new and changed Billing objects.
New and Changed Connect REST APIs in Billing
Improve checkout-to-cash operations for non-referenced refunds and unified checkout orchestration. You can also automate migration and invoicing workflows more effectively with enhanced scheduler controls, custom credit memo field support, custom billing cycle count, and flexible target-date billing behavior.
Changed Metadata Types in Billing
Enable billing forecasts by deploying and retrieving the org-level setting with Metadata API. Preview future invoice lines before posting to validate ramps, uplifts, amendments, and cancellations in advance.
New and Changed Invocable Actions in Billing
Automate refund and billing schedule workflows with a new invocable action, and get asynchronous execution support in existing invocable actions for billing schedule creation.
