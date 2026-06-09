---
page_id: cml_quote_group_ramp_segment_constraints.htm
title: Define Constraints for Quote Groups, Ramps, and Ramp Segments
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_quote_group_ramp_segment_constraints.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_group_type.htm
fetched_at: 2026-06-09
---

# Define Constraints for Quote Groups, Ramps, and Ramp Segments

Apply rules to quote groups, ramps, and ramp segments by using the
SalesTransactionItemGroup context tag. Assign a groupby value to messages defined in Constraint
Rules Engine to include the messages in custom grouping strategies.

- **[Define a Constraint for a Quote Group](./cml_quote_group_constraint.htm.md)**  
  To define a constraint for a quote group, use the require rule to assign the SalesTransactionItemGroup attribute that’s contained on a type to the value of the QuoteGroup container.
- **[Define a Constraint for a Ramp Group](./cml_ramp_group_constraint.htm.md)**  
  To define a constraint that applies to a ramp group, use the IsLineGroupRamped\_\_std attribute in the require rule to specify that the group is a ramp group.
- **[Define a Constraint for a Ramp Segment](./cml_ramp_segment_constraint.htm.md)**  
  To define a rule that applies to a ramp segment for defined conditions, use the ItemSegmentType attribute.
