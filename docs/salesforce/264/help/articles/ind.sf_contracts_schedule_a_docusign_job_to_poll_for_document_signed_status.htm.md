---
article_id: ind.sf_contracts_schedule_a_docusign_job_to_poll_for_document_signed_status.htm
title: Schedule a DocuSign Job to Poll for Document Signed Status
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_schedule_a_docusign_job_to_poll_for_document_signed_status.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_e-signature.htm
fetched_at: 2026-10-13
---

# Schedule a DocuSign Job to Poll for Document Signed Status

Salesforce Contracts provides an Apex class called EnvelopeStatusScheduler that you can schedule to poll DocuSign for statuses of envelopes submitted as part of the e-signature process.

The envelope details are enqueued iteratively to our messaging framework which handles updating the envelope status one at a time which also has a retry mechanism in case of specific failures during status updates.

If you schedule this class from the Salesforce UI, it can only be scheduled every hour (this is intended Salesforce behavior). However, you can schedule the class from the Developer Console at more frequent intervals. Since DocuSign places its own 15-minute minimum interval requirement in between two successive calls, the following example shows how to schedule using schedulers that run 15 minutes apart, so that four jobs are run every hour. You can run this with less number of schedulers if you want to poll DocuSign less frequently.

It is a Docusign API limitation that only allows polling of its resources at a 15-minute interval or more. The job will create four apex job schedulers that are 15 minutes apart. Therefore, the Docusign status poll can only occur at every 15-minute interval and it cannot occur at a lesser interval than that.

From the User menu, choose Developer Console.

The Force.com Developer Console window opens.

From the Debug menu, choose Open Execute Anonymous Window.

The Enter Apex Code dialog box opens.

Paste the following code into the Enter Apex Code dialog box:
ind_docgen_api.EnvelopeStatusScheduler envelopeScheduler = new ind_docgen_api.EnvelopeStatusScheduler();
System.schedule('Update Docusign Envelope Job 1', '0 0 * * * ?', envelopeScheduler);
System.schedule('Update Docusign Envelope Job 2', '0 15 * * * ?', envelopeScheduler);
System.schedule('Update Docusign Envelope Job 3', '0 30 * * * ?', envelopeScheduler);
System.schedule('Update Docusign Envelope Job 4', '0 45 * * * ?', envelopeScheduler);

Select the statement.
Click Execute Highlighted.
Close the Developer Console.
