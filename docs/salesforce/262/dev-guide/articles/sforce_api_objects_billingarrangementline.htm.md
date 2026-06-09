---
page_id: sforce_api_objects_billingarrangementline.htm
title: BillingArrangementLine
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_billingarrangementline.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# BillingArrangementLine

Represents the billing account, billing profile, and the percentage of
billing amount to be invoiced. Each billing arrangement line results in a separate invoice
addressed to the selected billing account. This object is available in API version
66.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| AccountId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Required. The ID of the account that's related to the billing arrangement line.  This field is a relationship field.  Relationship Name  Account  Refers To  Account |
| BillingAccountId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Required. The ID of the billing account record that's related to the billing arrangement line.  This field is a relationship field.  Relationship Name  BillingAccount  Refers To  BillingAccount |
| BillingArrangementId | Type  reference  Properties  Create, Filter, Group, Sort  Description  Required. The ID of the billing arrangement record that's related to the billing arrangement line.  This field is a relationship field.  Relationship Name  BillingArrangement  Relationship Type  Master-detail  Refers To  BillingArrangement (the master object) |
| BillingArrangementLineName | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort |
| BillingPercentage | Type  double  Properties  Create, Defaulted on create, Filter, Sort, Update  Description  Required. The percentage of the billing amount to be assigned to the billing account of the billing arrangement line. |
| ShouldBillRemainder | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the remainder percentage must be billed to the billing account of the billing arrangement line (`true`) or not (`false`).  The default value is `false`. |
| VersionNumber | Type  int  Properties  Filter, Group, Nillable, Sort  Description  A numerical value indicating the current version of the billing arrangement record. The version number increases when new billing arrangement line records are added or existing billing arrangement line records are updated. |
