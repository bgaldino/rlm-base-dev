---
article_id: ind.qocal_coterminate_contract_important_considerations.htm
title: Considerations for Contract Cotermination
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_coterminate_contract_important_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_coterminate_with_contract_end_date.htm
fetched_at: 2026-09-04
---

# Considerations for Contract Cotermination

Review the limitations and requirements for aligning subscription end dates with contract end dates to ensure successful sales and renewal processes. Reference these specifics when you build or troubleshoot transactions that use cotermination.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
Ramped Products Limitations

The following restrictions apply when you use cotermination with ramped products:

Users can’t add ramped products to a quote or order that references a contract with the cotermination flag set to True.
Assetization generates an error when an order attempts to assetize both a cotermed contract and ramped products.
