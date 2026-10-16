---
article_id: ind.sf_contracts_view_is_associated_with_clm.htm
title: View 'Is Associated With CLM'
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_view_is_associated_with_clm.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_system_administration_for_salesforce_contracts.htm
fetched_at: 2026-10-13
---

# View 'Is Associated With CLM'

The Is Associated With CLM field is associated with the Contract object. It indicates whether the contract record is created using the Salesforce Contracts application. The Is Associated With CLM field is automatically enabled when you create, import, or check out a contract document version from UI or using APIs.

Contract document generation and contract lifecycle management features are accessible only when the ContractManagement and DocGen licenses are enabled.

NOTE The contract Object State Definition is enforced only when the Is Associated With CLM field is enabled. By default, this field is not visible on the UI. The Is Associated With CLM field is automatically set to true during Import, Check out, or Generate actions.

To make the Is Associated With CLM field visible on the UI, perform these steps:

From Setup, click Object Manager.
Type Contract in the Quick Find box.
Click Contract and then click Fields & Relationships.
Click Is Associated With CLM and then click Set Field-Level Security.
From the Visible column select the users you want this field to be visible.
Save your changes.
Update the Page Layout configuration:
From Setup, click Object Manager.
Type Contract in the Quick Find box.
Click Contract and then click Page Layouts.
In the Quick Find box, search for Is Associated with CLM.
Drag and drop the field under the Contract Details section.
Save your changes.
View Is Associated With CLM on the UI:
Open a contract.
Click the Details tab to view the Is Associated With CLM checkbox.
