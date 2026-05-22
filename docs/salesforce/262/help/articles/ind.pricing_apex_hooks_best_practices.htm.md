---
article_id: ind.pricing_apex_hooks_best_practices.htm
title: Best Practices for Apex Pricing Hooks
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_apex_hooks_best_practices.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Best Practices for Apex Pricing Hooks

Follow these best practices when implementing Apex hooks in your pricing procedure plans to optimize performance and avoid unexpected results.

Use Leaner Queries

Avoid querying entire node tags. Instead, use leanerQueryTags to query only the specific attributes your hook needs. This reduces the amount of data loaded into the context and improves transaction processing speed.


String contextId = request.ctxInstanceId;
Context.IndustriesContext industriesContext = new Context.IndustriesContext();

Map<String, Object> inputTag = new Map<String, Object>();
List<String> tag = new List<String>();
tag.add('Contact_FirstName');
inputTag.put('contextId', contextId);
inputTag.put('tags', tag);
Map<String, Object> output = industriesContext.leanerQueryTags(inputTag);
   
NOTE Update your existing Apex pricing hooks to use leanerQueryTags instead of queryTags where possible.
