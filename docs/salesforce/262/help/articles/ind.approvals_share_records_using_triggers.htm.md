---
article_id: ind.approvals_share_records_using_triggers.htm
title: Share Temporary Access to Records in Advanced Approvals
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_share_records_using_triggers.htm&type=5&release=262
release: 262
release_name: Summer '26
area: approvals
fetched_at: 2026-05-12
---

# Share Temporary Access to Records in Advanced Approvals

Share temporary access to related records with your approvers by setting up triggers. After the approval action is complete, use a trigger to withdraw the record access.

When you submit a record for approval, the approver must have access to the record’s related object to perform actions on the approval request. If your object’s internal organization-wide sharing default is Private, you can use a trigger to create a share object that grants access to the approver. After the record is approved, you can withdraw the record access by using a trigger to delete the share record.

Create an Apex trigger to share access to a record's related object. Under Security, select the profile of your approver. See Define Apex Triggers.
TIP

If you're sharing access to a custom object, you can create an Apex sharing reason and include it in the trigger. An apex sharing reason restricts the record access to your specific use case.

Create an Apex trigger to delete the share record and revoke the record access after the approval request is complete. Under Security, select the profile of your approver.

You can customize the sample code snippet to suit your specific use case.

trigger AWIUpdate on ApprovalWorkItem(after update) {
List<ApprovalWorkItem> awiList = new List<ApprovalWorkItem>();
// Get the related opportunities for the accounts in this trigger
awiList = [SELECT Id, RelatedRecordId, AssignedToId FROM ApprovalWorkItem WHERE Id IN :Trigger.new];

for (ApprovalWorkItem awi : awiList) {
// Use the related record id, to delete the share record created for the user

Id relatedRecordId = awi.RelatedRecordId;
Id assignedToId = awi.AssignedToId;

SObjectType relatedRecordType = relatedRecordId.getSObjectType();
if (relatedRecordType.getDescribe().isCustom()) {
Map<String, Schema.SObjectType> tokens = Schema.getGlobalDescribe();
String relatedRecordShareName = relatedRecordType.getDescribe().getName().removeEnd('__c') + '__Share';
if(tokens.containsKey(relatedRecordShareName)) {
// Share object exists
SObject[] customShare = Database.query('SELECT Id FROM '
+ relatedRecordShareName + ' WHERE '
+ ' RowCause = \'AdvancedApprovalTriggerShareReason__c\' '
+ ' AND ParentId = :relatedRecordId'
+ ' AND UserOrGroupId = :assignedToId');
} else {
// OWD is Public Read Write
}
}
}
}
