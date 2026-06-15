---
article_id: ind.qocal_grant_binding.htm
title: Grant Binding
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_grant_binding.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Grant Binding

Grant binding determines how the grants of resources contained in an asset are pooled and consumed. In simpler terms, the binding decides whether a purchased service (like 1,000 text messages) is related to a single asset or shared across a wider group, such as an organization or a specific contract.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Binding Targets

When you add a quote line item or an order item to a quote or an order for usage-based products, you must select a binding target.

BINDING TARGET	DESCRIPTION
Self	The usage resources are bound to the asset itself. A standalone asset is created where the grants are only available to that specific line item. This is the default target for all usage products.
Product	The usage resources are bound to a product. An asset linked to the pack product or a line item can consume the resources.
Account	The usage resources are bound to a specific account. Multiple assets associated with the selected account can share the resources.
Contract	The usage resources are bound to a specific contract. Any asset linked to that contract can consume the resources.
Custom	The usage resources are bound to a custom object, if the standard options don’t fit the business model. Use the BindingObjectCustomExt object for custom object binding.
NOTE You can’t bind a commitment-based usage product to a target.

When you bind to a target and the order is activated, the consumption process creates a Usage Entitlement Account (UEA) record. This record acts as the container for the lifecycle of the service.

Multiple assets can be bound to the same target (for example, five different phones that use data service attached to the family account). The UEA tracks the validity period of the shared service by calculating the minimum start date and the maximum end date of all assets bound to that account. The UEA remains active as long as at least one asset bound to the target is active.

For every binding target and usage resource combination, the Usage Management process creates a wallet, which is tracked by the Usage Entitlement Bucket. Even if you buy multiple pack products, the total balance is aggregated and shown in this wallet.

IMPORTANT After an order is assetized, you can neither change the binding target nor move assets from one target to another.

When you bind multiple assets to the same target:

The product and price book entry associated with the usage entitlement account are determined by the first asset bound to the target.
The effective period for the bounded target is determined by the earliest start date and the latest end date of all associated assets.
The transaction usage entitlement associated with the parent usage entitlement is the first transaction usage entitlement created after the first product related to the bounded target is assetized.
EXAMPLE

To understand which binding type to select, let’s consider a company, Quantum Corp. The company purchases a communication suite that includes 500 SMS, 1,000 emails, and 10,000 API calls. Depending on their organizational needs, they can bind these grants in four ways:

Bind to Self (Asset Binding)—Quantum Corp buys a plan specifically for a remote contractor. The grants are bound to the individual asset. Only the contractor’s specific device can use these 500 SMS. In the Wallet view, the target is listed as Self.
Bind to Account—Quantum Corp wants their entire organization to share the resource pool and therefore, the grants are bound to the account. All departments, such as Sales, Marketing, and Finance that are associated with that account draws from the same 1,000 emails. The binding allows for resource sharing across multiple assets linked to an account.
Bind to Contract—Quantum Corp has a specific legal agreement for a three-year project. The grants are bound to the Contract ID. Any asset created under this specific contract draws from the 10,000 API calls. The binding makes sure that usage is strictly tied to the terms and duration of a specific legal entity.
Bind to Custom—Quantum Corp uses a multitenant cloud architecture. The grants are bound to a custom entity, such as a Tenant ID. This is used for specialized business models where resources must be isolated by a unique identifier other than a standard account or contract.
Rate Conflicts and Negotiation

A complexity arises when you attempt to bind multiple products to the same target that share the same resource, but have different negotiated rates.

EXAMPLE

If you bought a product bound to Account A with a negotiated rate of $0.80 per text, and later try to buy another product bound to Account A with a rate of $0.70 per text, it becomes a conflict.

To resolve the conflict, for a given resource and binding target combination, there must be a single agreed-upon rate. Usage Management automatically picks the cheapest rate available across multiple assets linked to the target. If a new asset or pack is purchased later, it overrides the existing rates.

SEE ALSO
Build a Quote for Usage-Based Products
