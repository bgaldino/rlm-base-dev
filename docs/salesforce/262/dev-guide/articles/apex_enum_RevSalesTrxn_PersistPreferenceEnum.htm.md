---
page_id: apex_enum_RevSalesTrxn_PersistPreferenceEnum.htm
title: PersistPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_RevSalesTrxn_PersistPreferenceEnum.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-06-09
---

# PersistPreferenceEnum Enum

Specifies whether to persist pricing changes for each sales transaction record.
Available in API version 65.0 and later.

## Enum Values

The `RevSalesTrxn.PersistPreferenceEnum` enum includes
this value.

| Value | Description |
| --- | --- |
| `Skip` | Skips the persistence of pricing changes for each sales transaction record. To persist pricing changes, specify `null` as the value in the method signature. If this value isn't specified, then request to persist pricing changes is performed by default. |
