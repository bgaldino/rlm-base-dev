---
article_id: ind.billing_dispute_management_resolve_service_requests.htm
title: Resolve Billing Service Requests
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_dispute_management_resolve_service_requests.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Resolve Billing Service Requests

When customers or service reps raise billing service requests or inquiries , Billing creates corresponding cases that are resolved by using the automated resolution actions. For specific service requests such as suspending billing, extending invoice due date, updating billing contact details, or correcting invoice charges, Billing automatically initiates the appropriate resolution associated with the service request. However, for any other billing inquiries that don’t have automated resolution, resolve the cases manually based on the business need and requirements.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To resolve service requests:	
Billing Customer Service User permission set
Unified Catalog Admin permission set
To resolve a case, open the case record on the Cases page.
If you have the case number, you can search the list of open cases for the specific case record. You can also view recent cases for the account on the Recent Billing Cases section to check whether similar cases were raised in the past and gather any historical information.
On the Billing Request tab, review the case details and any supporting documents or linked invoices.
Click Resolve Case, and then select the appropriate action based on the type of your request.
CASE REQUEST TYPE	RESOLUTION ACTION
Request to suspend billing	
Review the suspension and resumption dates, and revise as required, based on your company policies, if any.
Click Suspend Billing and then Finish.

Billing updates the invoice with the revised suspension and resumption dates, and the case is closed.


Request to update bill-to contact	
Review the revised bill-to contact and set it as default, if necessary.
Click Update Bill-to Contact and then Finish.

Billing updates the billing contact details and the case is closed.


Request to extend the invoice due date	
Review the current due date and set a revised due date based on your company policies, if any.
Click Extend Due Date, and then Finish.

Billing updates the invoice with the new due date and the case is closed.


Request to correct invoice charge dispute	
Review the disputed invoice lines in the invoice.
Edit the approved amounts for one or more invoice lines by updating the dispute record, and save your changes.
Select one or more dispute lines that you want to approve to issue a credit memo.
Click Next to submit the approved invoice lines for credit memo application, and then click Finish.

Billing generates a credit memo in Posted status and the case is closed.

Your customer can also view the updated case status on the Cases tab of the self-service Billing portal.

If necessary, you can change the status or priority of the case in the Additional Information section.

You can also use Billing Employee Assistance Agent to understand invoice charges and retrieve billing information.
