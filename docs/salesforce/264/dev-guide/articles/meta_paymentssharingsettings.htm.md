---
page_id: meta_paymentssharingsettings.htm
title: PaymentsSharingSettings
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_paymentssharingsettings.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_metadata_api_parent.htm
fetched_at: 2026-11-23
---

# PaymentsSharingSettings

Represents the settings to enable account-based sharing
to view details related to Revenue Cloud Billing on the objects for Payments and
Refunds.

Use account-based sharing to view Revenue Cloud Billing details on these
objects.

- Payment
- Payment Authorization
- Payment Authorization Adjustment
- Refund
- Saved Payment Method

## Parent Type and Manifest Access

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type and inherits its fullName
field.

In the package manifest, all the settings metadata types for the org
are accessed using the “Settings” name. See [Settings](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_settings.htm "HTML (New Window)") for more details.

## File Suffix and Directory Location

The PaymentsSharingSettings values are stored in the
PaymentsSharing.settings file in the
settings folder. The .settings files
are different from other named components, because there’s only one settings file
for each settings component.

## Version

PaymentsSharingSettings components are available in API version 64.0 and later.

## Special Access Rules

If you don’t have the View All Records
permission to the Payments and Refunds objects, then you can:

- View the records only when the records have a value for the
  Account field and a shared Account ID.
- Use Payment Sale API and Payment Authorization API irrespective of whether the
  Account ID is null or shared.
- Use Payment Capture API, Authorization Reversal API, Create Payment Refund
  Billing API, and Apply Refunds to Payments API only when the corresponding
  Authorization or Payment record has a shared Account ID.

See [Commerce Payments
resources](https://developer.salesforce.com/docs/atlas.en-us.264.0.chatterapi.meta/chatterapi/connect_resources_payments.htm "HTML (New Window)").

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| delegatePaymentSharingToAccount | boolean | Indicates whether sharing for these objects must be delegated to the corresponding Account record (`true`) or not (`false`). Payment, Payment Authorization, Payment Authorization Adjustment, Refund, or Saved Payment Method. The default value is `false`. If this field's value is set to `true`, you get access to these objects based on the access you have for the Account object. For example, if you have Read access to the Account object, you get Read access to the objects for Payments and Refunds. For saved payment method, the sharing is delegated to merchant account instead of account if the user has Manage Saved Payment Methods user permission. |

## Declarative Metadata Sample Definition

The
following
is an example of a PaymentsSharingSettings component.

```
<?xml version="1.0" encoding="UTF-8"?>
<PaymentsSharingSettings xmlns="http://soap.sforce.com/2006/04/metadata">
    <delegatePaymentSharingToAccount>true</delegatePaymentSharingToAccount>
</PaymentsSharingSettings>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>PaymentsSharing</members>
        <name>Settings</name>
    </types>
    <version>68.0</version>
</Package>
```

## Wildcard Support in the Manifest File

The wildcard character `*` (asterisk) in the
package.xml manifest file doesn’t apply to metadata types
for feature settings. The wildcard applies only when retrieving all settings, not
for an individual setting. For details, see [Settings](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_settings.htm "HTML (New Window)"). For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_paymentssharingsettings.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
