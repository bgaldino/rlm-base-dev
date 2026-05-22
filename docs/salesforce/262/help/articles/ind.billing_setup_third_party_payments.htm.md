---
article_id: ind.billing_setup_third_party_payments.htm
title: Set Up Third-Party Payment Gateways
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_third_party_payments.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Set Up Third-Party Payment Gateways

Bring your own third-party payment gateways to process payments and issue refunds. Set up and add external payment gateways, and then connect them to Billing.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with Revenue Cloud
The Salesforce Payments feature is available with the Revenue Cloud Billing license, with a cost per transaction model for both native and Bring Your Own payment gateways. Contact your Salesforce account executive for more information.
If you purchased the Revenue Cloud Billing license on or before July 2025, contact your Salesforce account executive to add the Salesforce Payments feature to your existing license.
USER PERMISSIONS NEEDED
To configure third-party payment features:	Payment Admin permission set
Initial Setup for Configuring Third-Party Payment Gateway

Before you configure third-party payment gateways, complete the preparatory tasks to establish a connection between your Salesforce org and your preferred third-party payment gateway. You need these details to get started.

An e-commerce merchant account and an API key
Apex classes adapters and the adapter name
Named credentials to authenticate your third-party payment gateway
A third-party payment gateway site that's registered in your Salesforce org
A Salesforce site that has access to the third-party payment gateway
Create an e-commerce merchant account in the third-party payment gateway that you want to implement.
Log in to your third-party payment gateway provider and add an e-commerce merchant account.
Navigate to the key management, developer, or advanced settings section of your chosen payment gateway platform, and generate an API key or secret key.

Your API key would look like: AQEvhmfxJ43HaxxHw0m/n3Q5qf3Ve4pBCIBMV3dVwyD4zesmTx/rk8/RZRz2w0bDdqMQwV1bDb7kfNy1WIxIIkxgBw==-C5bPe6tPCqOM35AEGroDa54J1Bl9AnsQKrDsDofVlrk=-i1ibf$Hu2v>8jR:Y9nU.

Note the merchant account user name and API key. You need them to create the named credentials.
Create your payment gateway Apex classes in your Salesforce org.
Obtain the adapter class details from your payment gateway provider or AppExchange.
To build and set up payment gateway adapters, see Payment Gateway Adapters. To define your Apex classes, see Commerce Payments namespace.
Save your Apex classes. Note the adapter name as you need it to create your payment gateway provider.
Create a legacy named credential in your Salesforce org to specify authentication parameters and the URL of your Apex callout endpoint.
Specify a user-friendly name for the label and a unique identifier for the name.
Enter the URL of your third-party payment gateway.
Select Named Principal as the identity type and Password Authentication as the authentication protocol.
Use your merchant account user name as the username. Use the API key as password as required by your payment gateway provider.
Save the named credentials as you need them to create your payment gateway.
Register your third-party payment gateway site in your Salesforce org to make sure that Apex callouts from the org to the payment gateway site are successful.
Enter a name and URL of your third-party payment gateway.
Mark the site as active and save your changes.
Add your third-party payment gateway URL as a trusted URL in your Salesforce org.
Enter an API name.
Enter the URL of your third-party payment gateway.
Mark the URL as active and save your changes.
Enable and set up your Salesforce site, so you can send and receive payments notifications from your third-party gateway.
Enter a label, name, and home page for your site.
Set the site’s public access settings to Guest Access to the Payments API.
Save your site details.
Configure Notification Settings on Your Third-Party Payment Gateway

The payment gateway uses a webhook to send notifications to your payment gateway adapter. A webhook is a combination of your site endpoint and the ID of the payment gateway provider. Create a webhook by providing a URL in the standard notification transport settings of your third-party payment gateway.

Use this URL for your site’s endpoint, replacing MyDomainName with your site's domain and URL. For example:
https://MyDomainName.my.salesforce-sites.com/solutions/services/data/v65.0/commerce/payments/notify
Find the ID of your payment gateway provider, and append the ?provider=ID query parameter to the endpoint. For example, https://MyDomainName.my.salesforce-sites.com/solutions/services/data/v65.0/commerce/payments/notify?provider=0cJR00000004CEhMAM
Enter the webhook in your third-party payment gateway’s standard notification settings.
Configure Payment Gateway Provider and Payment Gateway

Add a payment gateway provider after you set up your merchant account, your adapter classes, and your Salesforce site. Then, add a payment gateway on the payment gateway provider.

From Setup, in the Quick Find box, enter Billing, and then select Step 7: Payment Configurations in the Guided Setup.
Expand the Configure Third-Party Payment Gateways step, click Configure Payment Gateways, and then click Configure.
NOTE

For Salesforce orgs that are created in Winter ’26, the Configure Payment Gateways button in Step 7: Payment Configurations of the Billing Guided Setup, which redirects users to the Payment Gateway Configuration tab, is available by default. For Salesforce orgs that are created before Winter ’26, the Payment Gateway Configuration tab isn’t available by default. To fix this issue, change the settings of the Payment Gateway Configuration tab to Default On.

Complete these fields to create a payment gateway provider.
Enter a unique name and label for your payment gateway provider.
Select the Apex adapter class from the dropdown list.
Specify your required support for idempotency. For more details, see Idempotency Guidelines.
Save the payment gateway provider details.
Complete these fields to add a payment gateway.
Enter a unique name for your payment gateway.
Select a payment gateway provider from the dropdown list.
Select a named credential from the dropdown list.
Mark the status of your payment gateway as Active.
Save the payment gateway details.

If you already have an existing payment gateway provider, select Step 7: Payment Configurations in the Guided Setup, expand the Configure Third-Party Payment Gateways step, and click Configure Payment Gateways. On the Payment Gateway Configuration page, click Payment Gateways, and then click New. The configuration steps are the same.

Add Multiple Payment Methods

Configure support for payment methods such as Automated Clearing House (ACH), Single Euro Payments Area (SEPA), Bankers’ Automated Clearing Services (BACS), and Bulk Electronic Clearing System (BECS) on your third-party payment gateway. You can process payments, issue refunds, and view these saved payment methods in the Saved Payment Methods tab of your billing profile.

To add bank payment methods such as ACH, SEPA, BACS, and BECS, use the tokenizePaymentMethod API and set the bankType property in the bankPaymentMethod object to your chosen bank payment method.
To add card payment methods such as credit card or debit card, use the tokenizePaymentMethod API and set the cardCategory property in the cardPaymentMethod object.
SEE ALSO
Process Payments and Issue Refunds in Agentforce Revenue Management
