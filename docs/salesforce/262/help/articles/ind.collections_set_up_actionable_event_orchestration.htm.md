---
article_id: ind.collections_set_up_actionable_event_orchestration.htm
title: Set Up an Actionable Event Orchestration for Collections and Recovery
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_set_up_actionable_event_orchestration.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_customize_bre_components_to_determine_segment.htm
fetched_at: 2026-06-21
---

# Set Up an Actionable Event Orchestration for Collections and Recovery

Design an orchestration process that determines and updates collection plan segments for collection plan records in bulk. Help collections managers create tailored collection strategies, mitigate credit risk, and prioritize collection efforts according to different segments.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To create an actionable event orchestration:	

Actionable Event Orchestration Designer

AND

Actionable Event Orchestration Runtime

From the App Launcher, find and select Business Rules Engine.
From the app navigation menu, select Actionable Event Orchestrations.
Click New.
Specify the orchestration details.
Provide a name.
For actionable event type, find and select New Actionable Event Type. Specify an event type name and save the name.
For actionable event subtype, select New Actionable Event Subtype. Specify a name for the subtype, and find and select the actionable event type that you created in the earlier step.
Select Collection Plan as the usage type.
Select ExpressionSet-Based as the execution procedure type.
Select the event orchestration procedure that you cloned and customized earlier. See Clone and Customize the Prebuilt Expression Set Template for Collections.
Select the context definition that you cloned and customized earlier. See Clone and Customize the Prebuilt Context Definition for Collections.
Select the context mapping that you created earlier. See Clone and Customize the Prebuilt Context Definition for Collections.
Select Active.
Save your changes.
