---
page_id: actions_obj_review_approval_work_item.htm
title: Review Approval Work Item Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_review_approval_work_item.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Advanced Approvals
parent_page: advanced_approvals_invocable_actions_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Review Approval Work Item Action

Update an approval work item status with the assignee or reviewer's
            decision and any comments that the assignee or reviewer added.

        
            

Keep these considerations in mind when you use this invocable action.

            
                
- The user must be an assignee of the approval work item or be a member of a group
                    or queue if the approval work item is assigned to the group or queue.
                    Additionally, a user has access to Approval Submissions if they're a delegate of
                    the assignee or has a role higher than the assignee.

                
- The status of the approval work item must be in `Assigned` status.

                
- The user can also use this action if inherited access to group or queue
                    membership, nested group membership, roles hierarchy, or delegates is available.
                    See [Public Group
                        Considerations](https://help.salesforce.com/s/articleView?id=platform.user_groups_considerations.htm&language=en_US).

            

            

This action is available in API version 62.0 and later.

        

        
        

## Supported REST HTTP Methods

            
            
                
                    

**URI**

                    
: `/services/data/v68.0/actions/standard/reviewApprovalWorkItem`

                
                
                    

**Formats**

                    
: JSON, XML

                
                
                    

**HTTP Methods**

                    
: POST

                
                
                    

**Authentication**

                    
: `Authorization:
                            Bearertoken`

                
            

        

        

## Inputs

            
            

                    
                    
                    
                        
                            

                            

                        

                    

                    
                        
                            

                            

: 

: 

- 
- 

                        

                        
                            

                            

: 

: 

                        

                        
                            

                            

: 

: 

- 
- 
- 

                        

                        
                            

                            

: 

: 

                        

                    

                
| Input | Details |
| --- | --- |
| approvalDecision | **Type** string **Description** Required. Action that the assigned approver made for the approval work item. Valid values are: `approve` `reject` |
| approvalWorkItemId | **Type** string **Description** Required. ID of the approval work item to be reviewed by the assigned approver. |
| channelType | **Type** picklist **Description** Type of channel where the request to review the approval work item originated. Valid values are: `InvocableAction` `Slack` `ApprovalRecord` The default value is `InvocableAction`. Available in API version 65.0 and later. |
| comments | **Type** string **Description** Approval comments for the decision. |

        

        

## Outputs

None.

        
        

## Example

            
            
                
                    

**POST**

                    
: 
                        

Here's a sample request for the Review Approval Work Item action.

                        

```
{
  "inputs": [
    {
      "approvalWorkItemId": "9jRxx00000001lhEAA",
      "approvalDecision": "Approve",
      "channelType": "InvocableAction",
      "comments": "Looks good."
    }
  ]
}
```

                    

                    
: 
                        

Here's a sample response for the Review Approval Work Item action.

                        

```
{
  "actionName": "reviewApprovalWorkItem",
  "errors": null,
  "invocationId": null,
  "isSuccess": true,
  "outcome": null,
  "outputValues": null,
  "sortOrder": -1,
  "version": 1
}
```
