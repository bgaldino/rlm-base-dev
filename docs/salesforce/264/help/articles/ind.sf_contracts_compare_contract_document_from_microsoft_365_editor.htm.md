---
article_id: ind.sf_contracts_compare_contract_document_from_microsoft_365_editor.htm
title: Compare Two Versions of a Contract Document from the Microsoft 365 Editor
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_compare_contract_document_from_microsoft_365_editor.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_comparison_of_contract_document_versions.htm
fetched_at: 2026-10-13
---

# Compare Two Versions of a Contract Document from the Microsoft 365 Editor

Compare contract document versions directly from the Microsoft 365 editor during negotiations. Check out a document version, open the Salesforce Contracts Connector add-in, select the version to compare against, and review highlighted changes.

The Compare Contract Versions Enabled contract type config is created, and its value is set to Yes.

The Display alternative file previews setting is enabled. This setting must be enabled to view the comparison preview, which uses JPG file previews. See File Preview.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To compare contract document versions:	Microsoft 365 Word User
Check Out the contract document version by using the Modify Contract in Microsoft 365 Editor option.
A draft contract document version is created.
From the Home tab, open the Salesforce Contracts for Word add-in.
Click … and then select Compare Contracts.
The Selected Contract Version section shows the last checked-in document version, for example, version 6. The draft checkout version, for example, version 7, is selected by default in the Compare With dropdown.
In the Compare With dropdown, select the document version that you want to compare against; for example, version 5.
The right panel shows the selected version for comparison.
Turn on Show Differences.
Version comparison is a resource-intensive operation and may take some time. Make sure you’ve selected the appropriate contract version for comparison.
The system compares the two versions of the contract document and shows the differences in a new document on the right panel. It highlights the content edited, added, or deleted compared to the base version, which is document version 7.
To close the comparison window, click Cancel.

See Also

Create Contract Type Config to Compare Contract Versions

Compare Two Versions of a Contract Document from the Contract Record Page
