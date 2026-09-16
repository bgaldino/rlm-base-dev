---
article_id: ind.billing_payment_reconciliation_setup_vector_search.htm
title: Create a Vector Search Index
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_setup_vector_search.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_reconciliation_setup.htm
fetched_at: 2026-09-04
---

# Create a Vector Search Index

Enhance the searchability of your data by creating a vector search index on the Account object.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To create a vector search index:	

Data Cloud Architect permission set

For any data and query requirements, create a vector search index to enhance the searchability of your data.

Select Account as the source object.
On the chunking page, click Manage Fields and add Account Name.
The chunking strategy is autopopulated as Passage Extraction.
Click Next twice.
Review the configuration and target data model objects, and then save the search index.
Track the status of the search index and make sure it’s in Ready state.
NOTE Though the creation of a vector search index is a one-time task, make sure that you rebuild the vector search index when new accounts are added to the data streams.
