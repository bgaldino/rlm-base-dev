---
article_id: ind.qocal_ramp_deals_asset_considerations.htm
title: Ramp Deal Structure for Groups
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_ramp_deals_asset_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.understanding_ramp_deals.htm
fetched_at: 2026-09-04
---

# Ramp Deal Structure for Groups

Ramp deals contain time-bounded segments with distinct pricing, quantities, and discounts. The active structural mode dictates how you organize them.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.
Single-Level Structure (Default)

When only Ramp Deals for Groups in Quotes and Orders setting is turned on, the entire transaction is one implicit ramp schedule. Segments appear as a flat list of groups in the quote or order.

Quote or Order
└── Segment 1 (Group, Is Ramped = true)
└── Segment 2 (cloned from Segment 1)
└── Segment 3 (cloned from Segment 2)

This structure is the simpler of the two modes and works well when a deal has a single product set that ramps uniformly over time.

Two-Level Nested Structure

When the Multiple Ramp Schedules Per Transaction setting is also turned on, the quote or order supports up to 10 independent ramp schedules. Each schedule is a top-level Ramp Schedule Group, and its segments are subgroups nested within it.

Quote or Order
├── Ramp Schedule Group A
│   ├── Segment 1 (Subgroup)
│   ├── Segment 2 (Subgroup)
│   └── Segment 3 (Subgroup)
└── Ramp Schedule Group B
    ├── Segment 1 (Subgroup)
    └── Segment 2 (Subgroup)

Use this structure when different product sets in the same deal ramp on different timelines—for example, a software subscription that scales annually alongside a professional services package that ramps quarterly.

Key Objects
OBJECT	ROLE
Ramp Schedule Group	Top-level container for a ramp schedule (two-level mode only).
Segment (Group or Subgroup)	A single time period with its own pricing, quantity, and discount.
Quote Line Item / Order Product	A product line assigned to one or more segments.
Structure to Use
SCENARIO	RECOMMENDED STRUCTURE
Single product set, uniform ramp	Single-level
Multiple product sets with different ramp timelines	Two-level nested
Early renewal generating an auto-structured quote	Determined by the Multiple Ramp Schedules Per Transaction setting
NOTE All segments in a ramp schedule must share the same segment type. You can't combine Yearly and Custom segments in one schedule. The segment type you select for the first segment sets the type for the entire schedule.

To change it later, use Edit Ramp Schedule window to convert the whole schedule from Yearly to Custom, or from Custom to Yearly.
