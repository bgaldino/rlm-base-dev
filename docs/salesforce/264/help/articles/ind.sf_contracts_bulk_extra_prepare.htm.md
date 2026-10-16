---
article_id: ind.sf_contracts_bulk_extra_prepare.htm
title: Set Up Bulk Contract Extraction
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_bulk_extra_prepare.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_bulk_extra_overview.htm
fetched_at: 2026-10-13
---

# Set Up Bulk Contract Extraction

Bulk contract extraction uses Einstein Generative AI, Document AI, and Data Cloud.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To connect an external repository for bulk extraction:	

CLM Admin User

AND

Contracts AI User

AND

Data Cloud Architect

Before you begin: Provision Data Cloud in your org.

Enable Einstein Generative AI.
From Setup, in the Quick Find box, enter Einstein Setup, and then select Einstein Setup.
If you can’t find Einstein Setup, make sure that your org meets the prerequisites for the generative AI features that you plan to use. For more information, contact your Salesforce account executive.
Turn on Einstein.
Enable Contract Extraction.
From Setup, in the Quick Find box, enter Contracts AI, and then select Contract Extraction.
Turn on Contract Document Extraction.
The Document Extraction by Using Document AI option becomes available.
Turn on Document Extraction by Using Document AI.
The Bulk Extraction Configuration section becomes available.
Create and test a contract extraction template. See Configure Fields for Extraction with Contracts AI.

After you set up bulk extraction, connect an external repository to Data Cloud.
