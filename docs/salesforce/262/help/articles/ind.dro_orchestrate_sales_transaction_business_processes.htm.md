---
article_id: ind.dro_orchestrate_sales_transaction_business_processes.htm
title: Orchestrate Sales Transaction Business Processes
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_orchestrate_sales_transaction_business_processes.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Orchestrate Sales Transaction Business Processes

Set up a workflow to orchestrate business processes such as Quote to Order, Order to Cash, Incidents, Cases, Service Requests, and custom objects. First, extend the Sales Transaction context definition. Then, clone and save the required mapping, update the mapping to link the Sales Transaction node attributes to your business object's fields, create a procedure plan definition and associate it with the new context definition, and then configure the new context definition for the Sales Transaction Context Definition. Finally, submit the business process for orchestration.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management
USER PERMISSIONS NEEDED
To orchestrate business processes:	

Fulfillment Designer

OR

DRO Admin

Before you begin, align your business process with the predefined sales transaction context that’s used to map sales transactions to objects such as Quote, Asset, and Order. See Create Custom Context Definitions for Order Orchestration.

Extend the sales transaction context definition into a new context definition, map your object, to the new context definition, and activate the context definition. On the Context Definition Settings page, configure the activated context definition for the Sales Transaction context definition. See Create Custom Context Definition and Map Business Objects.
This step makes sure that the necessary data is retrieved throughout the various orchestration phases as steps progress.
Create a procedure plan definition for your business process and associate it with the new context definition.
Finally, submit your business process for orchestration. See Submit Sales Transaction Action.
Use the default StandardOrder adapter for submitting orders and the GenericAdapter for submitting any other business process for orchestration.
EXAMPLE A customer, Jones, places a service request for an electrical meter connection at their office. Here's how Dynamic Revenue Orchestrator (DRO) orchestrates the service request.

Step 1: Create Custom Objects

This step is necessary only if you are orchestrating a custom service request that can’t be processed using the out-of-the-box entities. Delivered objects generally have the capability to perform the necessary orchestration.

To effectively manage and track this custom service request, you must first set up these required custom objects in your Salesforce org.

CUSTOM OBJECT	CUSTOM OBJECT ROLE
Service Request	Captures the details of the customer's request for an electrical connection and stores information such as customer details, service location, requested service date, and status.
Service Request Item	Represents a specific item or component. A single service request can involve multiple items. For an electrical connection, service request items can include digging the service trench, connecting to the power grid, and testing the electrical panel.
Service Request Action	Tracks the various actions or tasks that must be completed to orchestrate the service request. Service request actions can include scheduling the site visit, dispatching a technician, installing the meter, and activating the connection.
Service Request Item Attribute	Stores additional attributes or details about the items involved in the service request. For example, for a meter installation, attributes can include the meter type, serial number, and voltage rating.
Service Request Item Relationship	Captures the relationships between different items or components of the service request. For example, the relationship can link the meter installation task to the specific meter that's installed.

Step 2: Extend the Sales Transaction Context Definition and Map the Service Request Entity

Next, extend the standard Sales Transaction context definition and name it DROServiceRequest. This extension helps you to include service-specific data in the orchestration process.

Now, map the fields of the Service Request object to the extended DROServiceRequest context definition. This mapping makes sure that the necessary service request data is available during the orchestration process.

You must map attributes such as Customer ID to ServiceRequest field’s CustID and Request Date to ServiceRequest field’s ReqDt.

Step 3: Create a Procedure Plan Definition

In this step, select the Service Request object as the primary object and associate it with the DROServiceRequest context definition. This procedure plan definition identifies the context definition that orchestrates the service request.

Step 4: Submit the Service Request for Orchestration

Finally, submit the service request for orchestration by using the Submit Sales Transaction invocable action. This action triggers the orchestration of the business object.

By processing these steps, DRO makes sure that the decomposition, plan composition, and plan execution occur in the correct sequence, ultimately creating a sales transaction fulfillment request to efficiently manage the electrical connection service. See Design Your Order Decomposition.
