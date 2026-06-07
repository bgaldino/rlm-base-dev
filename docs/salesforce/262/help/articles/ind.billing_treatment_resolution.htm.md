---
article_id: ind.billing_treatment_resolution.htm
title: Understand Billing Treatment Resolution
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_treatment_resolution.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing_policies_and_treatments.htm
fetched_at: 2026-05-11
---

# Understand Billing Treatment Resolution

The billing treatment field of an order product determines how it is billed. If the billing treatment is missing on the order product, an attempt is made to resolve the issue and assign an active billing treatment during the resolution.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Scenarios for Billing Treatment Selection

The billing policy for a product determines the billing treatment if it isn't explicitly defined for an order product. The billing admin defines billing treatments and a default billing treatment for a billing policy. The billing treatment is then assigned to the order product at runtime based on these scenarios.

Billing Treatment Selection	Scenario	Behavior
Default	An active default billing treatment is available for the billing policy.	Assigns the default billing treatment of the billing policy to the order product.
Manual	An active default billing treatment is available for the billing policy.	Assigns the default billing treatment of the billing policy to the order product.
Legal Entity	A legal entity is specified for the order product.	The order product’s legal entity is compared with the billing treatments in the billing policy. If a match exists, that billing treatment is assigned. Otherwise, the default billing treatment from the billing policy is used.
No legal entity is specified for the order product.	The default legal entity of the Salesforce org is compared with the billing treatments in the billing policy. If a match exists, that billing treatment is assigned. Otherwise, the default billing treatment from the billing policy is used.
Considerations

A default billing treatment is required when creating a billing policy. If a product doesn't have an associated billing policy, the default billing treatment defined for your Salesforce org is assigned. If no default billing treatment is defined for your Salesforce org, the billing calculation fails.

Only active billing policies and treatments are considered. If none exists, the billing calculation fails.
