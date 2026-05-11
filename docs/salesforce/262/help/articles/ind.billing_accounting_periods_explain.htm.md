---
article_id: ind.billing_accounting_periods_explain.htm
title: What are Accounting Periods?
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_accounting_periods_explain.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# What are Accounting Periods?

An accounting period is a specific time frame for which a company prepares its financial statements. For example, a month, quarter, or an year. It's a fundamental concept in accounting, as it dictates how and when revenue and expenses are recognized. Define start and end dates on the accounting periods to prevent overlaps or gaps and maintain a clean financial record for auditing purposes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
What are Legal Entity Accounting Periods?

While accounting periods define the overall timeframes, legal entity accounting periods represent the accounting period a legal entity uses for accounting.

Granular Reporting: Enables precise financial reporting tailored to the unique operational and legal requirements of each individual legal entity within your organization.
Transaction Assignment: Ensures that every billing transaction is directly tied to a specific legal entity and its corresponding legal entity accounting period. This ensures that a transaction initiated by a legal entity is recorded against that specific entity's books for a specific period.
Example: Streamlining Financial Closes for a Global Company

Imagine Innovate Solutions Corp., a global SaaS company with US, EU, and APAC legal entities, which struggled with manual financial closes, processing thousands of monthly billing transactions like invoices and payments. This led to extended monthly closes and audit challenges.

By using Agentforce Revenue Management's accounting period features, Innovate Solutions creates required records to automate their process:

Creating Accounting Periods: Innovate Solutions defines monthly, quarterly, and annual accounting periods to align with internal and external reporting cycles. For example, they create an Accounting Period for Q1 2027 with the start date as January 1, 2027, the end date as March 31, 2027, and the financial period as FY 2027.
Assigning Legal Entities to Accounting Periods: They assign specific legal entity to an accounting period for each subsidiary. For example, a Legal Entity Accounting Period record is created for Innovate Solutions EU - Jan 2027 linking to the Innovate Solutions EU legal entity and the Jan 2027 accounting period.
Automated Transaction Association: As new invoices, credit memos, and payments are processed, the system automatically assigned them to the correct legal entity accounting period based on the transaction's legal entity and effective date.

At the end of each month, Innovate Solutions Corp finalize and close their accounting records. SeeExample: Streamlining Accounting Period Closure.

SEE ALSO
Legal Entity Accounting Periods Closure and Reopening
