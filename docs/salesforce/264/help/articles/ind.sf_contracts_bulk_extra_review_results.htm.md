---
article_id: ind.sf_contracts_bulk_extra_review_results.htm
title: Verify Bulk Extraction Results and Create a Contract Record
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_bulk_extra_review_results.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_bulk_extra_overview.htm
fetched_at: 2026-10-13
---

# Verify Bulk Extraction Results and Create a Contract Record

Before creating contract records, validate the extracted data, such as contract details and clauses.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To review bulk extraction results:	

CLM Admin User

OR

CLM Runtime User

AND

Contracts AI User

AND

DocGen User

AND

Data Cloud User

From the App Launcher, open Contract Extraction Results.
Select Bulk Contract Extraction Results, and wait for the status of the contract to change to Review Not Started.
Review the extracted contract field values.
The extracted contract data appears in a layout that’s consistent with the record type in the associated extraction template.
NOTE If a field included in the extraction template doesn’t appear in the extraction results, confirm that you have the appropriate field-level security in your user profile or permission set. Missing fields are typically due to access restrictions, not the extraction model.
In the contract extraction results, click any record that you want to open.
On the Extracted Contract Fields tab, view the extracted values corresponding to a field.
Select the corresponding check to select a value.
If necessary, modify the extracted contract field values.
For example, update the contract term and the contract start date.
Make sure that all the required contract fields are populated
Save your changes.
Review the extracted clause content.
Click the Extracted Contract Clauses tab.
On the Extracted Contract Clauses tab, view the extracted clauses by clicking the  icon.
Use the dropdown actions to edit or delete the extracted clause.
If you’re satisfied with the extracted clause content and don’t want to make changes, click the pencil icon, and select Review Status.
After you validate the extracted content, you can create a Salesforce contract record with the extracted data. See Create a Contract Record.
Click Close.
SEE ALSO
Redraft Extracted Clause
Limitations of Field Values Extraction Using Contracts AI
