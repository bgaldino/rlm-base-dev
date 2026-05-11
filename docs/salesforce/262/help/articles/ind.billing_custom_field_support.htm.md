---
article_id: ind.billing_custom_field_support.htm
title: Capture Preferred Transaction Details by Using Custom Fields
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_custom_field_support.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing_setup.htm
fetched_at: 2026-05-11
---

# Capture Preferred Transaction Details by Using Custom Fields

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Capture Preferred Transaction Details by Using Custom Fields

To meet specific business requirements, populate custom field data from orders or external transactions to corresponding billing schedule, billing schedule group, and billing schedule group relationship records. Use Context Service to define how data must be transferred by configuring a custom intracontext mapping. Then, use the Create Billing Schedules for Orders API or the Create Standalone Billing Schedules API to generate billing schedules and billing schedule groups. You can also use custom fields to override the standard fields in billing nodes by using the custom intracontext mapping.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To select default records:	Billing Admin permission set

For example, you can create and map a custom field Purchase Order Number on an order object to a field named Purchase Order Number on the corresponding billing schedule object. Similarly, you can define and map a custom field Purchase Order Date on an order item to a Purchase Order Date field on the corresponding billing schedule group object.

Create the required custom fields on the billing schedule, billing schedule group, and billing schedule group relationship objects.
In Context Service, add the corresponding attributes and tag names to the extended context definitions.
Pass any preferred transaction data from orders to billing schedules by using the extended BillingContext context definition.
Pass transaction data from external transactions to billing schedules by using the StandaloneBillingContext context definition.
Map the corresponding attributes to the custom fields on the billing transaction nodes.
To capture preferred details from orders, edit the OrderEntities context mapping to map custom fields from the billing transaction context node attributes to the order fields.
To capture preferred details from any external transactions, edit the TransactionMapping context mapping to map the Transaction node attributes with external transaction fields.
Edit the BSGEntities context mapping to map the billing schedule context nodes to the fields of the billing schedule, billing schedule group, and billing schedule group relationship objects.
Add a custom intracontext mapping with the mapping intent set to Association. Add mappings from the billing schedule group, billing schedule, and billing schedule group relationship nodes to the corresponding billing transaction nodes.
BillingScheduleGroup node to the BillingTransaction node
BillingSchedule node to the BillingTransactionItem node
BillingScheduleGroupRelationship node to the BillingTransactionItemRelationship node
Activate the extended context definition.
Specify the custom intracontext mapping.
Before generate billing schedules from orders, select the custom intracontext mapping on the Billing Settings page in Setup.
Before you generate billing schedules from other internal or external transactions, specify the custom intracontext mapping name as the intraContext​CustomMapping​Name property value in the request body of the Create Standalone Billing Schedules API.
Generate billing schedules.
Use the Create Billing Schedules for Orders API for generating billing schedules from orders.
Use the Create Standalone Billing Schedules API for generating billing schedules from internal or external transactions, or CSV files.
The values in the custom fields are populated automatically.
SEE ALSO
Turn On Context Service
Select Context Definition and Mapping for Create Billing Schedules for Orders API
Revenue Cloud Developer Guide: Create Billing Schedules for Orders API
Revenue Cloud Developer Guide: Create Standalone Billing Schedules API
