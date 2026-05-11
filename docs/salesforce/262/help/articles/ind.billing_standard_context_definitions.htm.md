---
article_id: ind.billing_standard_context_definitions.htm
title: Standard Context Definitions for Billing
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_standard_context_definitions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing_configure_context_definitions.htm
fetched_at: 2026-05-11
---

# Standard Context Definitions for Billing

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Standard Context Definitions for Billing

After you turn on Context Service, you can access the standard context definitions that are available with Billing.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Agentforce Revenue Management


The BillingContext context definition is available with the Agentforce Revenue Management Advanced license or the Agentforce Revenue Management Billing license.

The StandaloneBillingContext context definition is available only with the the Agentforce Revenue Management Billing license. Contact your Salesforce account executive for more information.

Billing provides two standard context definitions. For optimal integration and a simplified setup, we recommend that you extend the standard context definitions and then use the extended context definitions.

BillingContext Context Definition

The Create Billing Schedules for Orders API uses the BillingContext context definition to hydrate the data of orders to create billing schedules. This context definition maps order data to structured billing configurations and has these mappings:

The OrderEntitiesMapping is the source mapping that maps Order fields to the billing transaction context nodes. The billing transaction nodes outline the structure, interpretation, and processing of billing-related data.
The BSGEntitiesMapping is the target mapping that maps the billing schedule context nodes to the fields of the Billing Schedule, Billing Schedule Group, and Billing Schedule Group Relationship objects. This mapping ensures that Order data is properly transferred to the appropriate Billing Schedule, Billing Schedule Group, and Billing Schedule Group Relationship fields.

On the Billing Settings page, select the extended context definition and context mapping that you want the Create Billing Schedules for Orders API to use.

IMPORTANT

From Summer ’25 and onwards, you will not be able to sync existing context definitions that were either cloned or extended from the standard BillingContext context definition. To fix this issue, use the Context Attribute Mapping API to delete duplicate BSGEntitiesMapping attribute mappings.

BillingTransactionSource attribute of the BillingSchedule node to Reference attribute of the BillingSchedule object.
BillingTransactionItemSource attribute of the BillingSchedule node to the ReferenceItem attribute of the BillingSchedule object.
StandaloneBillingContext Context Definition

The Create Standalone Billing Schedules API uses the StandaloneBillingContext context definition to hydrate the data of transactions to create billing schedules. This context definition has these mappings:

The TransactionMapping maps the fields of the transaction to the attributes of the Transaction node.
The BSGEntitiesMapping maps the attributes of the Billing Schedule, Billing Schedule Group, and Billing Schedule Group Relationship context nodes to the fields of the corresponding Salesforce objects.
