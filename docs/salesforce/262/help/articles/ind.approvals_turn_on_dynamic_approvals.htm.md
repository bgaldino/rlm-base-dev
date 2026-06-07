---
article_id: ind.approvals_turn_on_dynamic_approvals.htm
title: Set Up Dynamic Approval Notifications
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_turn_on_dynamic_approvals.htm&type=5&release=262
release: 262
release_name: Summer '26
area: approvals
fetched_at: 2026-05-12
---

# Set Up Dynamic Approval Notifications

To accelerate approval times, turn on Dynamic Approvals. This feature empowers approvers to make faster, data-driven decisions by embedding key insights directly into the request.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Agentforce Revenue Management with the Agentforce Revenue Management Growth or Agentforce Revenue Management Advanced license where Advanced Approvals and Einstein for Sales, Einstein for Platform, Einstein for Service, Einstein 1 Service, or Einstein GPT Service are enabled
IMPORTANT In order to use the AI generated email feature to approve or reject approval work items, your org must be provisioned with Data Cloud and Einstein. If you don’t have access to them, reach out to your Salesforce account executive.
USER PERMISSIONS NEEDED
To turn on dynamic approval notifications:	Approval Administrator
To receive AI-generated approval notifications:	Execute Prompt Template
From Setup, find and select Approval Settings.
Turn on Dynamic Approval Notifications.
When turned on, dynamic approval notifications are used in the body of approval emails of approval email templates. The prompt template that's provided in the org is the only one used with dynamic approval notifications.
EXAMPLE Let's consider a scenario where a manufacturing company uses dynamic approval notifications to streamline its quoting process. When a sales rep submits a quote, the sales manager receives an email that includes key data generated based on the step's approval conditions and user context, like the total quote amount and discount percentage, and features an AI-powered summary highlighting critical factors, such as low profit margins. The manager can then review all necessary context and approve or reject the quote directly from their email—without logging into another system. This process reduces approval times by 30% and ensures all decisions are fully informed.
