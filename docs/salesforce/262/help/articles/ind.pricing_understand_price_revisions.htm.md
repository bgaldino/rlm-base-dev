---
article_id: ind.pricing_understand_price_revisions.htm
title: Understand Price Revisions
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_understand_price_revisions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Understand Price Revisions

Price revisions are adjustments to the price of goods or services. For a sales rep, understanding these changes is crucial, as they provide a clear and logical justification for a new price during a renewal. These changes, whether increases (uplifts) or decreases, help companies respond to market shifts, control costs, and maximize revenue. Revisions aren't random; they're typically triggered by pre-planned schedules, shifts in economic indicators, or contractual terms, which allow a sales rep to frame a price adjustment as a pre-agreed condition rather than a surprise demand.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled

A common economic trigger is the Consumer Price Index (CPI), which gives a sales rep a powerful, objective tool for these discussions. Adjusting prices based on CPI is a primary way for businesses to handle inflation, ensuring their pricing keeps pace with the rising costs of goods and labor. By referencing a shared economic reality like the national CPI, a sales rep can depersonalize the price increase, anchoring the conversation in factual data and turning a potentially difficult negotiation into a transparent discussion about sustainability and fair value.

To make informed decisions about price revisions, you must understand two key entities.

Price Revision Policies. A price revision policy is a company's formal set of guidelines and formulas for modifying the prices of its products or services. It ensures that price adjustments are applied consistently and are based on predefined business rules rather than arbitrary decisions.

This policy can be applied at different levels: either granularly to a specific product or line item, or comprehensively across all products and services within an entire contract or quote. The policy's core is its formula, which often uses the Consumer Price Index (CPI) to account for inflation. These adjustments are typically made upon contract renewal, though they can also be performed annually on a separate schedule.

Index Rates. Using an index rate in pricing is a structured way to automatically adjust prices based on an external economic benchmark, most commonly the Consumer Price Index (CPI), which measures inflation. This data-driven approach ensures price changes are accurate and consistent. Its implementation depends on two key factors: using an official data source, like that from a national agency, and setting an update frequency. While annual updates offer predictability, more frequent adjustments, such as monthly, are common in high-inflation economies to keep pace with rising costs.

NOTE Custom profiles may not have access to these entities or its’ associated fields. Contact your Salesforce admin for help.
