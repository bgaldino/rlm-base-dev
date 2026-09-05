---
article_id: ind.qocal_ramp_deal_compound_uplift.htm
title: Set Up Ramp Deals with Standard or Compound Price Uplifts
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_ramp_deal_compound_uplift.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.setting_up_ramp_deals.htm
fetched_at: 2026-09-04
---

# Set Up Ramp Deals with Standard or Compound Price Uplifts

Salesforce admins configure either standard or compound price uplifts for ramp schedule groups so sales reps can quote multi-year deals. The uplift type selection determines a flat annual increase or an increase that builds on the prior segment's net price. Compound uplifts match how many enterprise customers negotiate multi-year contracts. They keep pricing transparent for approvers and remove the manual steps that lead to quoting errors and forecast drift.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.
USER PERMISSIONS NEEDED
To configure the default Ramp Uplift Type in Revenue Settings:	Customize Application
To set the Ramp Uplift Type on quote line groups:	Create on Quotes
To set the Ramp Uplift Type on order product groups:	Create on Orders

From Setup, in the Quick Find box, enter Revenue Settings, and select Revenue Settings. Then, turn on Advanced Detail Line Pricing. Set the default Ramp Uplift Type to standard or compound uplift.

Compound uplift calculations require this preference. If Advanced Detail Line Pricing is off, Salesforce doesn't show the compound option in the Ramp Uplift Type picklist or in the Default Ramp Uplift Type setting.

While in Revenue Settings, also turn on Ramp Deals for Groups in Quotes and Orders. The Ramp Uplift Type applies to group-based ramp deals. Set the Default Ramp Uplift Type to standard or compound. New ramp schedules inherit this default, but sales reps can override it at the ramp schedule group level.

Standard: Each segment's uplift applies to the original list price.
Compound: Each segment's uplift builds on the net price of the prior segment.

The prebuilt Revenue Management Default Pricing Procedure doesn't update automatically. If you use the prebuilt template, clone the latest template to apply the updates.

Follow Use Advanced Transaction Detail Line Pricing to Map Custom Fields and add another map line item mapping ItemApplUnitPriceUpliftPct__std to itemDetailApplUnitPriceUpliftPct__std to the prebuilt template.

From Setup, select Object Manager. Search for and select the quote or order object. Click Lightning Record Pages, then the quote or order record page. Click Edit to open Lightning App Builder. Select the Sales Transaction Line Editor (STLE) component to add the Ramp Uplift Type field to the quote line group and order product group. Add the Applied Unit Price Uplift field to the quote line item and the order product.

Synch the context definition before using compound uplift.
