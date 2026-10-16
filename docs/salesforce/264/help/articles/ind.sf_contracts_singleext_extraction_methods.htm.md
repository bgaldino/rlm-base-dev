---
article_id: ind.sf_contracts_singleext_extraction_methods.htm
title: Single Document Extraction Methods Fallback Behavior
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_singleext_extraction_methods.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_singleext_overview.htm
fetched_at: 2026-10-13
---

# Single Document Extraction Methods Fallback Behavior

Contracts AI provides different extraction methods to identify and pull data from uploaded documents. Each method has specific performance characteristics, and fallback behaviors.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions

The extraction method applies automatically based on enabled settings.

If Document AI is turned on, use Document AI for extraction.
If Document AI is turned on but can’t process the document because of an error, check whether Industries Einstein is turned on.
If Industries Einstein is on, use Industries Einstein to continue extraction.
If Industries Einstein isn’t on, use multimodal extraction.
If Document AI isn’t turned on, check whether Industries Einstein is turned on.
If Industries Einstein is on, use Industries Einstein for extraction.
If Industries Einstein isn’t on, use multimodal extraction.
If Document AI and Industries Einstein aren’t available or fails, then multimodal extraction becomes the final fallback method.
