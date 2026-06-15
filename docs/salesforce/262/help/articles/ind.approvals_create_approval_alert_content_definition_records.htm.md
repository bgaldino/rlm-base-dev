---
article_id: ind.approvals_create_approval_alert_content_definition_records.htm
title: Create Approval Alert Content Definition Records
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_create_approval_alert_content_definition_records.htm&type=5&release=262
release: 262
release_name: Summer '26
area: approvals
fetched_at: 2026-05-12
---

# Create Approval Alert Content Definition Records

To map a custom email template to notification reasons, create an approval alert content definition.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions where Advanced Approvals is enabled
USER PERMISSIONS NEEDED
To turn on email settings:	Customize Application
To create approval alert content definition records:	

Approval Admin

OR

Approval Designer

Before you begin, make sure that you complete these prerequisites.

Create email templates for different notification reasons for a given record. You can use a Lightning email template or a Visualforce email template. If you’re using a Visualforce email template, the recipient type must be User.
Turn on email notification settings.
Review these considerations for approval emails.
From the App Launcher, find and select Approvals.
Click Configure Approval Alerts.
Click New.
Enter a name for the record.
Enter your approval flow API name and the step API name.
If your email template is associated with the Approval Creation Success and the Approval Submission Approved or Rejected Status Update notification reasons, leave the step API name empty. These notification reasons apply to the entire workflow, not an individual step.
Under Email Template, enter the API name of your email template.
Select a notification reason.
Save your changes.
