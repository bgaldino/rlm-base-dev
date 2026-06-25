---
article_id: ind.collections_customize_actionable_event_orchestration_procedure.htm
title: Clone and Customize the Prebuilt Expression Set Template for Collections and Recovery
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_customize_actionable_event_orchestration_procedure.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_customize_bre_components_to_determine_segment.htm
fetched_at: 2026-06-21
---

# Clone and Customize the Prebuilt Expression Set Template for Collections and Recovery

Determine segments for collection plan records based on the collection plan object fields, such as due amount and days past due, and update the collection plan records with the segment values.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To clone and customize the expression set template:	Actionable Event Orchestration Designer

When you clone the prebuilt expression set template, DetermineCollectionPlanSegment, the steps from the template are copied to the first version of the cloned expression set by default. Link the decision matrix and the context definition that you cloned and customized earlier.

This event orchestration procedure gets the record details of collection plans in a loop, runs the decision matrix to determine the segment for each collection plan, and updates the segment value to the collection plan segment field value.

From the App Launcher, find and select Business Rules Engine.
From the app navigation menu, select Expression Set Templates.
Click DetermineCollectionPlanSegment.
From the Save As dropdown menu, select New Event Orchestration Builder.
Enter a name and rank, and save your changes.
The cloned actionable event orchestration automatically opens in the Event Orchestration Builder.
To link the newly created decision matrix, after the List operation component, click .
Find and select Lookup Table.
Find and select the decision matrix that you created earlier. See, Create a Decision Matrix to Determine Collection Plan Segments.
To map the decision matrix table variables to the associated context definition attributes, click Map Variables.
Map each lookup table variable.
From the Action menu, click Map.
Find and select the corresponding context definition attribute.
Click Done.
To set the start date time, click .
Select a start date and time.
Make sure that the start date and time of the event orchestration procedure is before the effective from date of the context definition that you cloned and customized earlier. See,

Clone and Customize the Prebuilt Context Definition for Collections.

Save your changes.
Close the Event Orchestration Builder.
From the App Launcher, find and select Business Rules Engine.
From the app navigation menu, select Event Orchestration Procedures.
Click the event orchestration procedure that you cloned and customized.
Click Edit.
Select the context definition that you cloned and customized earlier and save your changes. See Clone and Customize the Prebuilt Context Definition for Collections.
In the Expression Set Versions (n) section, click the version that you cloned and customized.
Click Activate.
