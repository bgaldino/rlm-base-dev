---
article_id: ind.sf_contracts_create_ps_for_external_credential_principal_access.htm
title: Create a Permission Set for External Credential Principal Access
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_ps_for_external_credential_principal_access.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_a_named_credential_and_external_credential_for_contracts_ai.htm
fetched_at: 2026-10-13
---

# Create a Permission Set for External Credential Principal Access

Create a permission set for the external credential principal access and assign the permission set to the autoproc user and the admin users responsible for initiating the contract extraction.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To enable Einstein and Contracts AI settings	

Contracts AI Clause Designer

AND

Prompt Template Manager

AND

NLP Service

AND

Scoring Framework Admin

From Setup, in the Quick Find box, enter Permission Sets, and then select Permission Sets.
Click New.
Enter your permission set name.
Save your changes.
Click External Credential Principal Access.
Click Edit.
Move the external credential principal from the Available to the Enabled column.
Save your changes.
Assign the new permission set to the autoproc user.
Open the permission set you created, and then copy the Id of the permission set from the URL.
It’s the alphanumeric string starting with OPS.
Open the Developer Console.
To open the Enter Apex Code window, click Debug | Open Execute Anonymous Window.
Paste the code and add the OPS string of the permission set ID.
insert new PermissionSetAssignment(
    AssigneeId = [SELECT Id FROM User WHERE alias = 'autoproc'].Id,
    PermissionSetId = '<OPS string>'
);
Click Execute.
The autoproc user is assigned the permission set that you created.
Assign the new permission set to the users who perform contract extraction.
From Setup, in the Quick Find box, enter Permission Sets, and then click Permission Sets.
Select the permission set you created.
Click Manage Assignments and then Add Assignments.
Select the checkboxes next to the names of the users you want to assign the permission set, and then click Next.
Click Assign.

See Also

Create Permission Sets
