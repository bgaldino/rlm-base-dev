---
article_id: ind.sf_contracts_initiate_private_external_review.htm
title: Initiate Private External Review
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_initiate_private_external_review.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_initiate_online_external_review_concept.htm
fetched_at: 2026-10-13
---

# Initiate Private External Review

Initiate a private external review and send a sanitized document copy to external reviewers. Internal comments and user details are removed to protect sensitive information. When the review is complete, changes are anonymized and access returns to the author.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To initiate an external online review:	

CLM Admin

OR

CLM User

OR

CLM Digital Experience Partner User

Prerequisites:

Make sure the contract is in Negotiating state for the Initiate External Review action to be available.
Make sure the document template doesn't contain shapes, because external private review won't work if shapes are present in the template.
Make sure the CLM admin has completed the configurations to enable private online external review. See Configure Private Online External Review.

To initiate a private external review.

Open the contract document version that you want to send for external review.
Select Initiate External Review from the Action drop down.
Select Initiate an Online Review, and then click Next.
Select Private Review, and then click Check Out Document.
To make the Add External Reviewers button active, refresh the page.
Click Add External Reviewers.
Type the email address of the user that you want to add as an external reviewer.
Select the access type for reviewer, such as edit and view. Click Add.
The view access type grants read-only access to the reviewers, while the edit access type enables the reviewers to modify the document, and to edit and delete their comments.
Click Send to start the review process.
The external reviewers are added to the document, and an email containing a link to access the document for third-party review is sent to the intended recipients.

Review a Contract Document in Private External Review Mode

Review a Contract Document in Private External Review Mode
As an external reviewer, access the contract document from your email invitation to edit clauses, add comments, tag co-reviewers, and track changes. When all reviewers finish, one reviewer marks the review as complete to return the document to the contract author.
Incorporate Reviewer Changes from Private External Review
After the external reviewers submit the reviewed document, the updated document with all changes is checked into Salesforce and made accessible only to the contract author. The external review changes are anonymized. The contract author receives an in-app notification and email confirming the completion of the external review and can then review the changes and finalize the updated document.
Restart Private External Review
Restart an external private review to begin the process again with a revised set of reviewers. A fresh document copy is created, previous reviewers and their changes are excluded, and the author must re-add all required reviewers.
