---
article_id: ind.billing_considerations.htm
title: Considerations When Setting Up and Using Billing
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing.htm
fetched_at: 2026-05-11
---

# Considerations When Setting Up and Using Billing

Before you set up and use Billing, keep these considerations in mind.

Coexistence with Subscription Management

You can’t turn on Billing when Subscription Management is enabled in your Salesforce org.

Impact of Turning Off Billing

If you set up Billing, and then turn it off:

You can't access any Billing features, including APIs and objects.
When you activate orders, billing schedules aren't created for order products.
Asynchronous API requests that are waiting to be dequeued and invoice runs that are queued before turning off Billing fail because the related Billing objects aren't accessible. In this scenario, Revenue Transaction Error Log records aren't created because the Billing objects they’re created for are no longer accessible.
If you turn off Billing before order activation and the initial orders don't have a billing treatment and a tax treatment, orders are activated without a billing treatment and a tax treatment. Else, they’re activated with the initial order's billing treatment and tax treatment.
If you turn off Billing after order activation and those orders don't have a related billing policy, Billing uses the default billing and tax treatments of your Salesforce org for those orders.
If you turn off Billing after order activation, billing schedules aren't created for any billing transactions.
Required Billing Permission Sets

To avoid facing access issues after turning on Billing and before setting up Billing features, assign the Billing Admin and Billing Operations User permission sets to users with the System Administrator profile.

See Assign Permissions to Access Billing Features.

Unsupported Orders

Billing also doesn't support Subscription Management orders.

Required Values for Order Activation

After turning on Billing, order activation succeeds only if the Order records have values for the Bill to Contact, Billing Address, and Shipping Address fields. Order activation fails if any of these values are missing.

Order Bill To Contact Field-Level Security

On enabling Billing, the field-level security for the Bill To Contact field of the Order object isn’t enabled automatically. You must manually set the field-level security before cloning the Billing context definition.

Designing Billing Policies

You must create and activate billing policies and their related records in this exact sequence because they’re inter-dependent:

Create draft billing policies.
Create the related billing treatments.
Create the related billing treatment items.
Activate the billing treatment items.
Activate the related billing treatments.
Activate the related billing policies.

See Define Billing Policies and Billability Rules.

Designing Tax Policies

You must create and activate tax policies and their related records in this exact sequence because they’re inter-dependent:

Create draft tax policies.
Create the related tax treatments.
Activate the tax treatments.
Activate the related tax policies.

See Define Tax Calculation for Invoices.

Default Values

The default billing treatment, tax treatment, and legal entity selected on the Billing Settings page are applicable only to Billing.

See Select Default Billing Treatment, Tax Treatment, and Legal Entity.

Supported Languages

The Billing user interface is available in English and all the fully supported languages.
