---
article_id: ind.collections_run_actionable_event_orchestration.htm
title: Run the Actionable Event Orchestration by Using Connect API
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_run_actionable_event_orchestration.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_customize_bre_components_to_determine_segment.htm
fetched_at: 2026-06-21
---

# Run the Actionable Event Orchestration by Using Connect API

Use the /connect/orchestration/inbound-events Connect API to determine collection plan segments by using the actionable event orchestration you created earlier.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To run an actionable event orchestration using the Connect API:	Actionable Event Orchestration Runtime
From Setup, in the Quick Find box, enter Decision Tables, and then select Decision Tables.
Click Filter and Match Actionable Event Orchestrations.
Click Refresh.
Run the endpoint /services/data/v62.0/connect/orchestration/inbound-events and specify the parameters.
{
"sourceSystemIdentifier": "CollectionAEOId",
"type": "CollectionEvent",
"subtype": "CollectionPlanEvent",
"eventData": "{\"CollectionPlan\":[{\"id\":\"1EuZ6000000CaRqKAK\",\"businessObjectType\":\"CollectionPlan\"}]}"
}
For sourceSystemIdentifier, specify the name of the actionable event orchestration.
For type, enter the event type that you created earlier.
For subtype, enter the event subtype that you created earlier.
For eventData, enter the ID of the Collection Plan object.
For businessObjectType, enter Collection Plan.
