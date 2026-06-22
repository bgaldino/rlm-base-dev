---
article_id: ind.collections_customize_bre_components_to_determine_segment.htm
title: Set Up Rule-Based Collection Segmentation
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_customize_bre_components_to_determine_segment.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup.htm
fetched_at: 2026-06-21
---

# Set Up Rule-Based Collection Segmentation

Enable Business Rules Engine components, and configure them to determine the segments for collection plans. Collections includes DetermineCollectionPlanSegment, which is a prebuilt event orchestration procedure that helps you determine and update the collection plan segments for collection plan records in bulk. The prebuilt event orchestration procedure references various prebuilt Business Rules Engine components, such as context definition, decision matrix, and actionable event orchestration expression set. Clone and configure these components according to your business needs.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.

Watch this video to understand how to segment overdue accounts by using business rules.

If you aren’t able to watch the video in full screen, open the video on a new tab: Rule-Based Segmentation for Collections.

Enable Business Rules Engine Components for Collections and Recovery
Enable the Business Rules Engine components to allow users to access and configure context definitions, expression sets, and lookup tables, which helps you to determine the segments for collection plans.
Clone and Customize the Prebuilt Context Definition for Collections and Recovery
To pass the context of a Collection Plan record to related Business Rules Engine components to determine the collection plan segment, clone and customize the prebuilt context definition, CollectionPlanSegmentContext.
Create a Decision Matrix to Determine Collection Plan Segments
Implement business rules to determine a collection plan segment for a collection plan according to your business requirements.
Add the Collection Plan Segment Picklist Values
Add the picklist values for the collection plan segment field on the Collection Plan object by using the collection plan segment values that you created earlier using the decision matrix.
Clone and Customize the Prebuilt Expression Set Template for Collections and Recovery
Determine segments for collection plan records based on the collection plan object fields, such as due amount and days past due, and update the collection plan records with the segment values.
Set Up an Actionable Event Orchestration for Collections and Recovery
Design an orchestration process that determines and updates collection plan segments for collection plan records in bulk. Help collections managers create tailored collection strategies, mitigate credit risk, and prioritize collection efforts according to different segments.
Run the Actionable Event Orchestration by Using Connect API
Use the /connect/orchestration/inbound-events Connect API to determine collection plan segments by using the actionable event orchestration you created earlier.
