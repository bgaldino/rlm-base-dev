---
article_id: release-notes.rn_transaction_management_changed_connect_rest_apis.htm
title: Changed Connect REST API in Transaction Management
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_transaction_management_changed_connect_rest_apis.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_transaction_management.htm
fetched_at: 2026-09-30
---

# Changed Connect REST API in Transaction Management

Use the enhanced Read Sales Transaction API to discover available batches, then retrieve only the batches that you need in parallel.

Changed Connect REST API Request Body
Read Sales Transaction Input
This request body has these new properties.
batchIndices—List of batch indices to fetch. The indices are zero-based. If you include this property, the API returns only the specified batches. This property supports fetching multiple batches in parallel.
shouldReturnMetadataOnly—Indicates whether to return only batch metadata without fetching batch data (true) or not (false).
