---
article_id: ind.collections_create_decision_matrix_for_segment.htm
title: Create a Decision Matrix to Determine Collection Plan Segments
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_create_decision_matrix_for_segment.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_customize_bre_components_to_determine_segment.htm
fetched_at: 2026-06-21
---

# Create a Decision Matrix to Determine Collection Plan Segments

Implement business rules to determine a collection plan segment for a collection plan according to your business requirements.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To create, update, and delete decision matrices and matrix versions:	Rule Engine Designer
To use decision matrices in Business Rules Engine:	Rule Engine Runtime

Here’s an example of a decision matrix that determines a collection plan segment based on current due amount and days past due. Create a decision matrix according to your business requirements.

DAYS PAST DUE	CURRENT DUE AMOUNT	COLLECTION PLAN SEGMENT
90	2000	High Balance Delinquent
30	300	Low Balance Delinquent

When you create a decision matrix, keep these considerations in mind.

Plan your decision matrix structure before creating the matrix. After you choose the type of a decision matrix, you can’t change the type.
Before you create a decision matrix, make sure you understand its functionality and nuances of the decision matrix.
Create a standard decision matrix.
Make sure that the column names of the decision matrix are distinct from the tag names in the context definition that you cloned and customized previously.
If your decision matrix has only a few rows of data, create a standard decision matrix manually.
If you're dealing with sizable data, use a CSV file to create a decision matrix.
