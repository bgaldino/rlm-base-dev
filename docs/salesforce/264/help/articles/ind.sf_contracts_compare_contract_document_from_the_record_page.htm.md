---
article_id: ind.sf_contracts_compare_contract_document_from_the_record_page.htm
title: Compare Two Versions of a Contract Document from the Contract Record Page
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_compare_contract_document_from_the_record_page.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_comparison_of_contract_document_versions.htm
fetched_at: 2026-10-13
---

# Compare Two Versions of a Contract Document from the Contract Record Page

Use the Compare Contracts feature to analyze differences between document versions. You get a clear, side-by-side comparison of the modifications, including edits, additions, and deletions.

The Compare Contract Versions Enabled contract type config is created, and its value is set to Yes.

The contract has at least two versions in DOCX format.

The contract document versions you want to compare are checked in.

The Display alternative file previews setting is enabled. This setting must be enabled to view the comparison preview, which uses JPG file previews. See File Preview.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To compare contract document versions:	

CLM Admin

OR

CLM Runtime User

NOTE Version comparison doesn't work if the document is downloaded using Download for External Review, and re-uploaded with the "externalReview_" prefix. To resolve this, remove the prefix before uploading the document or use the standard Download icon.
Open a contract, click the Documents tab, and then click .
In the Console app, the contract view defaults to the expanded view.
Click View Documents and make sure that the .docx document is selected.
If a .pdf file is selected, the Compare Contracts button is inactive.
Click Compare Contracts.
The Selected Contract Version section shows the document version that you selected for comparison; for example, version 7.
In the Compare With dropdown, select the document version you want to compare against; for example, version 5.
Version comparison is a resource-intensive operation. Wait for the system to generate the differences preview.
The right panel loads the selected version for comparison.
Verify that you have selected the correct version, and then turn on Show Differences.
The system compares the two versions of the contract document and shows the differences in a new document on the right panel. It highlights the content edited, added, or deleted compared to the base version, which in this instance is document version 7.
To close the comparison window, click Cancel.

See Also

Create Contract Type Config to Compare Contract Versions

Compare Two Versions of a Contract Document from the Microsoft 365 Editor
