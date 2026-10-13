---
article_id: ind.sf_contracts_set_up_the_remote_site.htm
title: Set Up the Remote Site for Salesforce Contracts E-Signature
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_set_up_the_remote_site.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_workflow_to_setup_esignature_for_contract_object.htm
fetched_at: 2026-10-13
---

# Set Up the Remote Site for Salesforce Contracts E-Signature

To configure DocuSign to work with the Salesforce Contracts application, you must connect Salesforce to a DocuSign account. You set up the DocuSign remote site as one of the websites your Salesforce org can invoke.

ATTENTION Since DocuSign places a 15-minute minimum interval requirement between two successive calls, Salesforce strongly recommends that you maintain a separate DocuSign account for each org. Sharing a DocuSign account between orgs can cause DocuSign processing delays.

To set up the remote DocuSign site:

From Setup, in the Quick Find box, enter Remote Site Settings.
Click Remote Site Settings.
Click New Remote Site.
Enter these details:
Remote Site Name: {Add a remote site name}
Remote Site URL: Your company’s DocuSign URL. For example, https://www.docusign.net.
Save your changes.
