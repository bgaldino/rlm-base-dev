---
article_id: ind.collections_risk_score_set_up_copy_enrichment.htm
title: Create a Copy Field Enrichment to Copy Risk Score from Data Model Object
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_risk_score_set_up_copy_enrichment.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_risk_scores.htm
fetched_at: 2026-06-21
---

# Create a Copy Field Enrichment to Copy Risk Score from Data Model Object

To copy risk score data from the Collection Plan Data Model Object to the risk score field in the Collection Plan Salesforce object, create a Copy Field Enrichment.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To view enrichments in Setup:	View Setup
To create or update enrichments:	

Customize Application AND Data Cloud User AND Write Access to Data Action AND Write Access to Data Space Definition

If you enabled enhanced security data spaces, you also need the permission Customize Data Actions on the Dataspace Scope.

Create a Data 360 Copy Field Enrichment to copy risk score from Collection Plan Data Model Object to risk score field of the Collection Plan object in your org. When creating a copy field enrichment, make sure that you select these options:
Data Space: The custom data space that you created earlier.
Data 360 Object: Specify the name of the Data 360 object that is created at run time during the Tableau Next app installation. This object is named in the format: <AppName> Risk Score. For example, if you have named the app as Collections, the Data Model Object name is Collections RiskScore.
Target Object: Collection Plan
Data 360 Copy Field: Risk Score
Make sure that you start the sync operation after you create the copy field enrichment for collection risk score data.
SEE ALSO
Salesforce Help: Enrichment Troubleshooting
