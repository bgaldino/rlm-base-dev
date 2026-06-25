---
article_id: ind.collections_customize_flows_outbound_calls.htm
title: Customize Prebuilt Flows for Outbound Collections Dialer
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_customize_flows_outbound_calls.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_outbound_dialer.htm
fetched_at: 2026-06-21
---

# Customize Prebuilt Flows for Outbound Collections Dialer

Clone and customize the prebuilt flows to determine how your collections campaign calculates representative availability, updates call details, and routes voice calls. These prebuilt flows manage the end-to-end outbound calling process, from initiating campaign calls to tracking rep status upon call completion.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To customize the prebuilt flows:	

Collections and Recovery Admin permission set

AND

Customize Application permission

Collections and Recovery includes seven prebuilt flows that helps you to automate outbound calling to delinquent borrowers.

FLOW NAME	FLOW TYPE	TRIGGER
Determine Collections Rep Availability	Auto-Launched flow	Triggered by the flow, Create Collections Rep Availability Event
Create Collections Rep Availability Event	Auto-Launched flow	

Triggered by these flows:

Update Collections Campaign Voice Call Details
Check Collections Rep Availability on Call Completion
Check Collections Rep Availability On Voice Call Readiness

Update Collections Campaign Voice Call Details	Record-Triggered flow	The flow is triggered when a voice call record is created or updated.
Check Collections Rep Availability on Call Completion	Record-Triggered flow	The flow is triggered when an agent work record created or updated.
Check Collections Rep Availability On Voice Call Readiness	Record-Triggered flow	The flow is triggered when a user presence record is created or updated.
Update and Route Collection Campaign Call	Omni-Channel flow	Reference this flow when configuring Omni-Channel Unified Routing for the Amazon contact center.
Initiate Collections Campaign Calls	Schedule-Triggered flow	NA
Determine Collections Rep Availability

The flow calculates the number of Collections representatives available to handle outbound calls by retrieving real-time metrics for all online reps, currently occupied reps, and queued or dialed call volume. Clone, customize, and activate this flow.

From Setup, in the Quick Find box, enter Flows, and then select Flows.
Click Determine Collections Rep Availability.
From the action menu, click Save As New Flow.
Enter flow label and API name, and save the changes. Note the cloned label and API name for future reference.
Activate the flow.
Create Collections Rep Availability Event

The flow creates an event to notify Collections rep availability by checking if at least one Collections rep is online and available. Sets the event’s CampaignIdentifier to the actionableListId passed into the flow if a voice call queue exists. Otherwise, it sets the identifier to Null. Clone, customize, and activate this flow.

From Setup, in the Quick Find box, enter Flows, and then select Flows.
Click Create Collections Rep Availability Event.
From the action menu, click Save As New Flow.
Enter flow label and API name and save the changes. Note the cloned label and API name for future reference.
Edit the flow to update the subflow element that calls the Determine Collections Rep Availability flow. Update this reference to use the label of the cloned Determine Collections Rep Availability flow.
Find the subflow element that is calling the flow, Determine Collections Rep Availability. Make sure that you note the label and API name of this subflow element.
Delete this element and re-insert the subflow element in the same position.
Click the newly added subflow element.
Search for the label of the cloned Determine Collections Rep Availability flow, and select it.
Enter the exact label and API name that you copied earlier in step a for the new subflow element, and then save the changes.
If you modify this label and API name, make sure that you update all references to it within the flow.
Save the changes.
Activate the flow.
Update Collections Campaign Voice Call Details

The flow updates the Collections Campaign Call details, such as call connection status and voice call ID. The flow then calls the Create Collections Reps Availability Event subflow, which creates a Collections Reps Availability Event by checking if at least one Collections Rep is online and available. Clone, customize, and activate the flow.

From Setup, in the Quick Find box, enter Flows, and then select Flows.
Click Update Collections Campaign Voice Call Details.
From the action menu, click Save As New Flow.
Edit the flow to update the subflow element that calls the Create Collections Rep Availability Event flow. Update this reference to use the label of the cloned Create Collections Rep Availability Event flow.
Find the subflow element that calls the flow, Create Collections Rep Availability Event. Make sure you note the label and API name of this Subflow element.
Delete this element and re-insert the Subflow element in the same position.
Click the newly added Subflow element.
Search for the label of the cloned Create Collections Rep Availability Event flow, and select it.
Enter the exact label and API name that you copied earlier in step a for the new Subflow element, and then save the changes.
If you modify this label and API name, make sure that you update all references to it within the flow.
Save the changes.
Activate the flow.
Check Collections Rep Availability on Call Completion

When a Collections rep closes an assigned call, the flow runs a subflow that checks if at least one rep is online and available to create a Collections Rep Availability Event. Clone, customize, and activate the flow.

From Setup, in the Quick Find box, enter Flows, and then select Flows.
Click Check Collections Rep Availability on Call Completion.
From the action menu, click Save As New Flow.
Edit the flow to update the Subflow element that calls the Create Collections Rep Availability Event flow. Update this reference to use the label of the cloned Create Collections Rep Availability Event flow.
Find the Subflow element that calls the flow, Create Collections Rep Availability Event. Make sure you note the label and API name of this Subflow element.
Delete this element and re-insert the Subflow element in the same position.
Click the newly added Subflow element.
Search for the label of the cloned Create Collections Rep Availability Event flow, and select it.
Enter the exact label and API name that you copied earlier in step a for the new Subflow element, and then save the changes.
If you modify this label and API name, make sure that you update all references to it within the flow.
Save the changes.
Activate the flow.
Check Collections Rep Availability On Voice Call Readiness

When a Collections rep is eligible to take a voice call, and creates a Collections Reps Availability Event by checking if at least one Collections Rep is online and available. Clone, customize, and activate the flow.

From Setup, in the Quick Find box, enter Flows, and then select Flows.
Click Check Collections Rep Availability On Voice Call Readiness.
From the action menu, click Save As New Flow.
Edit the flow to update the Subflow element that calls the Create Collections Rep Availability Event flow. Update this reference to use the label of the cloned Create Collections Rep Availability Event flow.
Find the Subflow element that calls the flow, Create Collections Rep Availability Event. Make sure you note the label and API name of this Subflow element.
Delete this element and re-insert the Subflow element in the same position.
Click the newly added Subflow element.
Search for the label of the cloned Create Collections Rep Availability Event flow, and select it.
Enter the exact label and API name that you copied earlier in step a for the new Subflow element, and then save the changes.
If you modify this label and API name, make sure that you update all references to it within the flow.
Save the changes.
Edit the Start element, and Set the Service Presence Status ID field to the ID of the Available for Voice status. To get the status ID:
From Setup, in the Quick Find box, find and select Presence Statuses.
Click Available for Voice.
Copy the URL.
Identify the Status ID by extracting the alphanumeric string that follows %2F prefix in the URL. For example, if the URL is https://app.cumuluscloud.com/lightning/setup/ServicePresenceStatus/page?address=%2F0N5SB000000WzEr, then the Status ID is 0N5SB000000WzEr.
Save the changes, and activate the flow.
Update and Route Collection Campaign Call

The flow updates the voice call record with the collection plan details, and directs a voice call to a routing queue. Clone, customize, and activate the flow.

From Setup, in the Quick Find box, enter Flows, and then select Flows.
Click Update and Route Collection Campaign Call.
From the action menu, click Save As New Flow.
Activate the flow.
Initiate Collections Campaign Calls

The flow iterates over all collection plans linked to the actionable list, confirms Collections Rep availability, and initiates a Collections call. Clone, customize, and activate the flow.

From Setup, in the Quick Find box, enter Flows, and then select Flows.
Click Initiate Collections Campaign Calls.
From the action menu, click Save As New Flow.
Enter a unique API name, and save the changes.
Provide values to these input variables.

actionableListId: The ID of the actionbale list that contains a set of collection plans identified for the call outreach activity.

campaignBatchSizeLimit: The total number of members allowed in a Collections Campaign batch. By default, this is set to 200.

campaignDurationInHours: The numerical value representing the maximum duration allowed for a Collections campaign, measured in hours. By default, this is set to 9.

routingQueueId: The ID of the routing queue that contains Collections voice calls.

contactCenterId: The ID of your Salesforce contact center set up for Amazon Connect.

contactFlowId: The ID of the contact flow—not the full Amazon Resource Name (ARN). Get this value from your Amazon Connect instance.

outboundPhoneNumber: The phone number used to make the outbound call, such as your Customer Service phone number claimed by your Amazon Connect instance.

queueId: The ID of the holding queue to which you want to transfer these outbound calls.

Schedule the flow by updating the start date, start time, and frequency in the start element.
Save the changes and activate the flow.
A Collections campaign is created with the details provided, and starts the outbound calling activity for these campaign members.
