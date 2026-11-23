---
article_id: ind.collections_edit_deployment_for_event_action.htm
title: Customize the Preconfigured Action Launcher Deployment and Enable Interaction Summaries
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_edit_deployment_for_event_action.htm&type=5&release=264
release: 264
release_name: Winter '27
area: collections
parent_article: ind.collections_setup_interaction_outcome.htm
fetched_at: 2026-11-23
---

# Customize the Preconfigured Action Launcher Deployment and Enable Interaction Summaries

Edit the Collection Plan Processes deployment in Action Launcher to include the Capture Collections-Related Interaction quick action. Then, turn on Interaction Summary to view customer interactions on a collection plan record page.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To edit the preconfigured Action Launcher deployment:	

Industry Service Excellence

AND

Collections and Recovery Admin

Create a global quick action to send email. Create Send Email global action.When creating the action, set these values.
Action Type: Send Email
Target Object: Outgoing Email
Label: Email
Name: SendEmail
Create a global quick action to create a record. Create a global action to create a record.When creating the action, set these values.
Action Type: Create a Record
Target Object: Note
Label: New Note
Name: NewNote
From Setup, in the Quick Find box, enter Action Launcher, and then click Action Launcher.
Click the action menu on the Collection Plan Processes deployment, and select Edit.
Select Buttons, flows, links, and quick actions, and click Next.
Click Next.
On the Select actions to add window, find and select these quick actions, and click Next.
Capture Collections-Related Interaction
Send Email
Create a Record
To view customer interactions on the collection plan record page, turn on Interaction Summary.
From Setup, in the Quick Find box, enter Interaction Summary, and then select Interaction Summary Settings.
Turn on Interaction Summary.
Save the changes.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.collections_edit_deployment_for_event_action.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
