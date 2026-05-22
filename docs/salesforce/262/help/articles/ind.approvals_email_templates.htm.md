---
article_id: ind.approvals_email_templates.htm
title: Email Templates in Advanced Approvals
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_email_templates.htm&type=5&release=262
release: 262
release_name: Summer '26
area: approvals
fetched_at: 2026-05-12
---

# Email Templates in Advanced Approvals

In an approval workflow, a request passes through multiple stages and reviewers. To provide reviewers and submitters clear and contextual information in their emails, create custom email templates for different notification reasons.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions where Advanced Approvals is enabled

With Lightning or Visualforce email templates, use advanced formatting capabilities that help organize details for complex records, such as quotes. The formatted template helps the reviewer review all the necessary details to act on the request directly from their email.

Create an email template for each of these notification reasons in an approval workflow. The template defines the specific trigger event that sends the email to the reviewer and the submitter. A reviewer can be a user, group, or queue.

NOTIFICATION REASON	DEFINITION
Approval Step Assignment	The reviewer is notified about the approval step.
Approval Step Reassignment	The new reviewer is notified about the approval step.
Approval Step Assignment to Delegate	The delegate of the reviewer is notified about the approval step.
Approval Step Reassignment to Delegate	The delegate of the newly assigned reviewer is notified about the approval step.
Approval Creation Success	The submitter is notified about the creation of the approval submission.
Approval Submission Approved or Rejected Status Update	The submitter is notified about the approval or rejection on the related approval submission.
Approval Work Item Approved or Rejected Status Update	The submitter is notified about the approval or rejection on the related approval work item.
Auto-Approval Confirmation	The reviewer is notified about the auto-approval of the resubmitted record.

After you create the email templates, create approval alert content definition records. These record defines the association between your email template and notification reason within an approval step or the entire workflow.

Create Approval Alert Content Definition Records
To map a custom email template to notification reasons, create an approval alert content definition.
SEE ALSO
Considerations for Emails in Advanced Approvals
