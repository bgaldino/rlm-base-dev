---
article_id: ind.sf_contracts_create_a_custom_report_type_and_build_a_report_for_clause_history.htm
title: Create a Custom Report Type and Clause History Report
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_a_custom_report_type_and_build_a_report_for_clause_history.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_document_clause_library.htm
fetched_at: 2026-10-13
---

# Create a Custom Report Type and Clause History Report

Create a custom report type with the Document Authored Content object to run reports on clause metadata. Add fields from contracts, clauses, and clause sets to customize the report layout, then build a report for detailed clause analysis.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To configure a custom report type:	CLM Admin
From Setup, in the Quick Find box, enter Report Types, and then select Report Types.
Click Continue.
Click New Custom Report Type.
Enter the values for the custom report type.
Select Document Authored Content as the Primary Object.
The Document Authored Content object represents the metadata of the content within a document's content boundary, such as a template or contract document. With the document authored content, you can store the metadata details of the marked clauses and sections in Salesforce.
Enter a label for the report type.
Users see this label when they create reports, such as All Clauses Report.
Enter a unique name for the report type.
Enter a description.
Users see this description when they create reports.
In Store in Category, select Other Reports.
The category determines the folder where your users find the custom report type when they create approval history reports.
Select In Development as the deployment status.
To provide all users access to the report type, select Deployed.
Click Next.
Save your changes.
Select the fields that you want to show in your report.
Click Edit Layout.
Click Add fields related via lookup.
Click Reference Object by Document Template.
Select Name.
To add the contract fields, click Reference Object by Contract Document Version.
Select Contract, and then click view related fields.
Select Activated Date, Contract ID, Contract Name, Contract Number, Contract Type, and Status.
Click OK.
Click Add fields related via lookup >>.
To add the document clause fields, click Standard Content Object >>.
Select Content, Document Clause ID, Format, Is Alternate Clause, Language, Name, Status, and Version.
To add the clause set details to the report, select Document Clause Set, and then click view related fields.
Select Default Language, Document Clause Set ID, Name, and Status.
Select Content Document, and then click view related fields.
Select Versioning Policy, and Title.
Click OK.
To view the clauses that have parent clauses, click Parent Content.
Select Checksum, Document Authored Content Identifier, and Name.
Save your changes.
Build the report.
From the App Launcher, find and select Reports.
Click New Report.
Click Other Reports.
Select your report type, and then click Start Report.
The report opens in edit mode and shows a preview.
Customize your report until it shows the data that you need. .
Add, and remove fields to your report as columns. Group by rows and columns, filter report data, and add a chart. Customize your report until it shows the data that you need. See ​Build a Report in Lightning Experience​ and ​Sample Clause Report
Save your changes.
If this report is new, give it a name and, optionally, a description. With access and sharing in mind, save the report in an appropriate folder.
To view the report results, click Run.

See Also

Reports

Document Authored Content

Sample Clause Report
Add fields to your report as columns, group by rows and columns, filter report data, and add a chart. Then customize your report to view the desired clause data.
