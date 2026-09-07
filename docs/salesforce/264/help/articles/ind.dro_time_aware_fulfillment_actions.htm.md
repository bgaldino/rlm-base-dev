---
article_id: ind.dro_time_aware_fulfillment_actions.htm
title: How Dynamic Revenue Orchestrator Determines Actions for Time-Aware Assets
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_time_aware_fulfillment_actions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_time_aware_fulfillment.htm
fetched_at: 2026-09-05
---

# How Dynamic Revenue Orchestrator Determines Actions for Time-Aware Assets

When you turn on time-awareness, Dynamic Revenue Orchestrator (DRO) evaluates the state of a Fulfillment Asset (FA) record and its Fulfillment Asset State Period (FASP) records before and after technical assetization, along with any attribute changes. DRO then determines the decomposition action for a given period.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
BEFORE TECHNICAL ASSETIZATION	AFTER TECHNICAL ASSETIZATION	FA ATTRIBUTE/QUANTITY CHANGE	ACTION	EFFECT
FA	FASP	FA	FASP
Doesn't exist	Not applicable	Exists	Exists	Not applicable	Add	Creates an FA and an FASP.
Exists	Doesn't exist	Exists	Exists	Not applicable	Renew	Adds an FASP to an existing FA.
Exists	Exists	Exists	Doesn't exist	Not applicable	Cancel	A new FASP superseeds the existing one.
Exists	Exists	Exists	Exists	Changes present	Amend	A new FASP superseeds the existing one.
