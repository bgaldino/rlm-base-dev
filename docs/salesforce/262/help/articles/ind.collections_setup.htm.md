---
article_id: ind.collections_setup.htm
title: Set Up Collections and Recovery
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_setup.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections.htm
fetched_at: 2026-06-21
---

# Set Up Collections and Recovery

Assign users the required permission sets and object permissions. Use the preconfigured Action Launcher deployment to help your collections specialists quickly launch Collections actions. Clone and customize the prebuilt Business Rules Engine components to determine collection plan segments. Customize prebuilt flows that help your collections specialists ‌streamline collection activities. Customize prebuilt flows that automate case creation and closure. Create an actionable list definition by using the Collection Plan and related objects, and help your collections managers create prioritized lists of collection plan records and assign them to collections specialists. Configure MuleSoft integration to submit a direct debit request.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
Billing Considerations for Collections and Recovery
Use of certain Collections and Recovery feature impacts the consumption of credits used for billing in these usage types.
Assign Object Permissions for Collections and Recovery
To set up and configure Collections in your Salesforce org, assign the relevant object permissions.
Configure Action Launcher Deployment for Collections and Recovery
Use the preconfigured Action Launcher deployment for Collections to help your collections specialists launch actions related to Collections. Make the Action Launcher component available to your users by adding the component to the collection plan Lightning record page.
Enable Timeline for Collections and Recovery
Configure interactive timelines so that collections specialists and collections managers can view the key events related to collections on the timeline.
Show Account and Contact Details on a Collection Plan Page
Enable the View Account and Contact Details setting so that your collections specialists and collections managers can view the account and contact information for person accounts in a single, unified view.
Set Field-Level Security for Case Source
Give collections specialists read and edit access to Case Source field so they can create a case for a collection plan.
Add Related Cases to Collection Plan
The Related Cases tab on the collection plan details page helps collections specialists to quickly view the cases associated with the collection plan. Add the Cases related list to the collection plan page layout.
Set Up Case Management for Collections and Recovery
To automatically create and close cases for collection plans, set field-level security for the case source field, create a decision matrix, and customize the prebuilt flows for case creation and closure.
Set Up Rule-Based Collection Segmentation
Enable Business Rules Engine components, and configure them to determine the segments for collection plans. Collections includes DetermineCollectionPlanSegment, which is a prebuilt event orchestration procedure that helps you determine and update the collection plan segments for collection plan records in bulk. The prebuilt event orchestration procedure references various prebuilt Business Rules Engine components, such as context definition, decision matrix, and actionable event orchestration expression set. Clone and configure these components according to your business needs.
Set Up Actionable Segmentation for Collections and Recovery
Enable Actionable Segmentation, which helps you segment similar client profiles, curate them, and design timely and personalized client outreach programs. Create actionable list definitions by using the Collection Plan and related objects. Your collections managers can use these list definitions to create prioritized lists of collection plans, and plan collections activities more effectively.
Set Up Promise to Pay
Customize the prebuilt flow that helps collections specialists create promise to pay agreements for borrowers. A Promise to Pay is a commitment by the delinquent borrower or customer to pay a specified amount by a certain date.
Configure Additional Payment Options for Collections and Recovery
Set up Salesforce Pay Now and customize the prebuilt flows that enable collections specialists to generate payment links and send the links to borrowers.
Configure Automatic Payment Status Notifications
Customize the prebuilt flow to automatically send payment status emails to customers. To use this flow, make sure that you have set up Data 360 and Marketing Cloud in your org.
Set Up Mulesoft Integration for Direct Debit Request
Help your collections specialists ‌submit a direct debit request to the core banking system. Collections specialists can request for a direct debit using the Request Direct Debit bulk action on a collections actionable list page. The action initiates a new debit from the customer’s mandated bank account.
Setup and Configuration for Capturing Customer Interaction Outcomes
The prebuilt action, Capture Collections-Related Interaction, helps collections specialists to capture collections-related interactions and the next steps. For example, a collections specialist can use this action to record an interaction with a borrower after discussing ‌a disputed collection amount that requires investigation. They can also use the action to create a case, and case proceeding records. To set up this action and related flows, add picklist values for the relevant fields on the Collection Plan, Case, and Case Proceeding objects, create object field aliases, customize the prebuilt expression set, and configure field-level security.
Setup and Configuration for Call Compliance Checks
Collections specialists can make informed decisions about contacting borrowers by using call compliance checks. Turn on Financial Account Management Standard Objects, and Context Definitions.
Configure Automatic Payments Received Updates
Automatically update payments received in collection plans and payment schedules. Customize the Collections: Update Payment Details prebuilt flow. This flow is triggered automatically when a payment intent event is created for a successful transaction.
Import Collection Data From CSV Files
Easily input large amounts of collection data into Salesforce standard and custom objects by using CSV files. Help users transform data from various sources or formats into a standardized structure. Import collection data from external systems into the Collection Plan and related objects with minimal errors and reduced data entry time.
Customize Lightning Pages to View Collection Plans and Related Records in a Hierarchical View
To enable collections specialists to view collection plans and their related records, add the Hierarchical View component to the financial account record page.
Set Up Collection Campaigns
Create data streams, identity resolution rulesets, data graphs, and segments by using the Collections Data Kit so that collections managers can easily use collections data to create and manage collection campaigns, track the campaign's performance, and notify customers of their payment status.
Set Up Account Summary for Collections and Recovery
Add custom fields to the Account object to store collections summary of all the collection plans associated with an account. Clone and customize the predefined Data Processing Engine definition to compute the aggregated summary of specific collection plan fields. Clone and customize the prebuilt Flexcard to show the aggregated collections summary. Customize the Lightning pages to view the Collections Summary, and all the collection plans linked to an account.
Set Up Document Generation Templates for Collections and Recovery Communication
Enable Design Document Templates, clone and customize predefined document generation templates, and generate collections-related documents by using these templates.
Set Up Payment Plans to Manage Financial Hardships
Help your customers manage their financial hardship situations effectively by setting up payment plans based on their financial account types and debt situations. Enable Decision Table Access, define payment plan types, create a decision table for payment plan mapping, and create an expression set from the prebuilt expression set template to reference payment plan mapping decision table.
Set Up Tableau Next App to Predict Risk Scores for Collections and Recovery
A risk score for a collection plan predicts the likelihood of a borrower not repaying their outstanding debt. It helps businesses prioritize and tailor their collection efforts. A higher risk score typically indicates a lower probability of payment, while a lower score suggests a higher likelihood of repayment. Set up Data 360, add Data Cloud Salesforce Connector permissions, install, and configure a Tableau Next app by using the prebuilt Collections Risk Scoring template configuration type in the Scoring Framework setup. Schedule the prebuilt data transform to compute risk scores on latest collection plans. Create a Copy Field Enrichment to copy the risk score from a Data 360 object to the risk score field of the Collection Plan Salesforce object.
Set Up Outbound Dialer for Collections and Recovery
Automate outreach to delinquent borrowers by setting up the Outbound Dialer for Collections. Configure Salesforce Voice with Amazon Connect (formerly Service Cloud Voice with Amazon Connect), and use the prebuilt Data Processing Engine definition to create actionable lists of overdue collections. Then, clone and customize the prebuilt flows that manage the end-to-end outbound calling process, from initiating campaign calls to tracking rep status upon call completion.
