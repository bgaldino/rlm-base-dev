---
article_id: ind.collections_assign_object_permissions.htm
title: Assign Object Permissions for Collections and Recovery
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_assign_object_permissions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup.htm
fetched_at: 2026-06-21
---

# Assign Object Permissions for Collections and Recovery

To set up and configure Collections in your Salesforce org, assign the relevant object permissions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To view object settings:	View Setup and Configuration
From Setup, in the Quick Find box, enter Profiles, and then select Profiles.
Click the profile that you plan to edit.
Click Edit.
Go to Administrative Permissions, and select View Setup and Configuration.
Under Standard Object Permissions, locate these objects and assign permissions according to the profiles.
PROFILE	TASK	OBJECT	PERMISSIONS
Collections managers	To create prioritized lists of collection plans	
Actionable List
Actionable List Column
	Read, Create, Edit, and Delete
Collections managers	To create prioritized lists of collection plans	Action List Member	Read, Create, Edit, Delete, and View All Records
Collections managers	To view the borrower details on the collection plan record details page	Financial Account	Read, Create, Edit, Delete, and View All Records
Collections specialists	To view the borrower details on the collection plan record details page	Financial Account	Read, Create, Edit, and Delete
Collections managers	To view the details on the collection plan record details page	
PartyIncome
PartyExpense
	Read, Create, Edit, Delete, and View All Records
Collections specialists	To view the details on the collection plan record details page	
PartyIncome
PartyExpense
	Read, Create, Edit, and Delete
Collections managers	To view collection plan details	
Collection Plan
Collection Plan Item
Collection Plan Reason
	Read, Create, Edit, Delete, and View All Records
Collections specialists	To create a promise to pay record	
PaymentSchedule
PaymentScheduleItem
Collection Plan
Collection Plan Item
	Read, Create, Edit, and Delete
Collections specialists	To create case, case proceeding, and case proceeding participant records	
Case
CaseProceeding
CaseProceedingParticipant
	Read, Create, Edit, and Delete
Collections specialists	To create payment plans to manage financial hardship situations	
PaymentSchedule
PaymentScheduleItem
PaymentScheduleDistributionMethod
PaymentScheduleTreatment
PaymentScheduleTreatmentDetail
Collection Plan
Financial Account
	Read, Create, Edit, and Delete
