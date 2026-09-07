---
article_id: ind.approvals_email_notification_behavior.htm
title: Considerations for Emails in Advanced Approvals
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_email_notification_behavior.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_advanced_approvals_considerations.htm
fetched_at: 2026-09-07
---

# Considerations for Emails in Advanced Approvals

Keep these considerations in mind when working with approval emails and notifications.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled
To enable approval email notifications, turn on Send Approval Work Item Assignment Emails and Send Approval Submission Status Email Notifications in Advanced Approval settings, and deselect Don’t send approver notifications in the approval step of your workflow.
To use the email templates that you create, make sure that they’re marked as Available for Use.
The entity of the email template must match the target object of the approval workflow.
You can create only one email template for a given combination of approval flow, approval step, and notification reason.
An email template associated with the approval alert content definition record overrides the custom email specified for an approval step within the workflow.
A template that isn’t associated with a specific step is applied to all steps in the workflow that lack a unique template.
If your email template uses an Apex controller, grant the Automated Process user access to the Apex class. Without this access, the custom template isn’t applied.
When reviewers respond by email, they must place the decision keyword such as Approve on the first line and their comment on the second line. Otherwise, the comment isn’t captured.
Queue emails can be sent to a maximum of 1,000 recipients. To avoid exceeding this limit, enable Send approval work item emails only to queue members. This restricts emails to queue members and prevents them from being sent to users higher in the role hierarchy.
If the org reaches its email limit, users don’t receive approval emails until the cool-down period resets or the limit is increased.
Emails sent after a reassignment may include the extra word "null" in the body. You can ignore this text.
When Advanced Approval Delegation is enabled, delegates receive email notifications when approval work items are assigned or reassigned to them.
