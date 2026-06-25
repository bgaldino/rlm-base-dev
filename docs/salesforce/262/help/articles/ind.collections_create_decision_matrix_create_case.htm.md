---
article_id: ind.collections_create_decision_matrix_create_case.htm
title: Create and Activate a Decision Matrix to Create a Case for a Collection Plan
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_create_decision_matrix_create_case.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_configure_case_management.htm
fetched_at: 2026-06-21
---

# Create and Activate a Decision Matrix to Create a Case for a Collection Plan

Create a decision matrix with the collection plan reason code, case reason, case priority, and case type parameters. The decision matrix updates the case field values automatically when a case is created for a collection plan.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To create, update, and delete decision matrices and matrix versions:	Rule Engine Designer
To use decision matrices in Business Rules Engine:	Rule Engine Runtime

Here’s an example table that lists a few of the collection plan reason codes and their descriptions.

COLLECTION PLAN REASON CODE	REASON	DESCRIPTION
CPR01	Missed payments	The borrower has missed one or more payment deadlines, and the outstanding amount is more than 60 days past the due date.
CPR02	Bounced checks	Payments made by the borrower have been returned due to insufficient funds or other issues.
CPR03	High-risk borrower	The borrower has a history of making late or partial payments due to seasonal income or low credit scores.
CPR04	Deceased account	Delinquent or missed payments due to the borrower’s unexpected death.
CPR05	Bankruptcy	The borrower has experienced a significant change in their financial situation, such as a job loss or business shut down, or a medical emergency, affecting their ability to repay.

Here’s an example of a decision matrix that lists probable case reason, case priority, and case type based on the collection plan reason code. Create a decision matrix according to your business requirements.

CODE	REASON	PRIORITY	TYPE
CPR01	Missed Payments	Medium	Collections
CPR02	Bounced Checks	High	Collections
CPR03	High-Risk Borrower	Medium	Collections
CPR04	Deceased Account	High	Collections
CPR05	Bankruptcy	High	Collections

When you create a decision matrix, keep these considerations in mind.

Plan your decision matrix structure before creating it.
Before you create a decision matrix, make sure you understand its functionality and nuances.
Create the decision matrix with the name, DetermineCaseReasonAndRelatedAttributes.
Create the first column with header type as Input and name it as Code. The code values that you enter here must map to the code values of the Collection Plan Reason object.
Create the second column with header type as Output and name it as Reason. This reason column maps to the Reason field of the Case object.
Create the third column with header type as Output and name it as Priority. This priority column maps to the Priority field of the Case object.
Create the fourth column with header type as Output and name it as Type. This type column maps to the Type field of the Case object.
If your decision matrix has only a few rows of data, create a standard decision matrix manually.
If you're dealing with sizable data, use a CSV file to create a decision matrix.
