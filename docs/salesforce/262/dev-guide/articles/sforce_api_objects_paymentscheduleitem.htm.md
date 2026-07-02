---
page_id: sforce_api_objects_paymentscheduleitem.htm
title: PaymentScheduleItem
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentscheduleitem.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PaymentScheduleItem

Represents information about a payment to be processed. Each schedule
item can have different payment configuration fields, such as payment methods, payment
dates, and payment accounts. When a payment scheduler launches a payment run, the run
evaluates active payment schedule items, and picks them up for payment processing if they
match the scheduler’s payment criteria. This object is available in API version 64.0
and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Payment Admin permission set or the
Payment Operations User permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| AppliedAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount of a credit memo or payment that’s applied to the parent reference entity and is excluded for payment collection. |
| Comments | Type  textarea  Properties  Create, Filter, Nillable, Sort, Update  Description  Additional details about the payment schedule item. |
| LastPaymentGatewayLogId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The most recent payment gateway log created after a payment gateway request is sent to process a payment based on the payment schedule item.  This field is a relationship field.  Relationship Name  LastPaymentGatewayLog  Refers To  PaymentGatewayLog |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, and LastReferenceDate is not null, the user accessed this record or list view indirectly. |
| NextPaymentRetryTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort  Description  The slated time of the next payment retry for the payment schedule item. Available in API version 66.0 and later. |
| NextPaymentRetryTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort  Description  The slated time of the next payment retry for the payment schedule item. Available in API version 66.0 and later. |
| PaymentAccountId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The account assigned to payments made from the payment schedule item. When a payment schedule item is created, its PaymentAccountId inherits the payment schedule’s DefaultPaymentAccountId. However, you can provide a new PaymentAccountId at any time. If you change the PaymentAccountId, only payments made after the change use the new account.  This field is a relationship field.  Relationship Name  PaymentAccount  Refers To  Account |
| PaymentBatchRunId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The payment batch run that evaluated the payment schedule item for payment processing.  This field is a relationship field.  Relationship Name  PaymentBatchRun  Refers To  PaymentBatchRun |
| PaymentGatewayErrorCategory | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The category of payment gateway errors for the payment schedule item.  Valid values are:  - `CardLimit`—Card   Limit Decline - `GatewayConnection`—Gateway Connection   Error - `PaymentInformation`—Invalid Payment   Details - `PaymentProcessing`—Payment Processing   Error - `Security`—Security Failure - `Unknown`—Unknown   Error - `ValidationFailure`—Internal Validation   Error  Available in API version 66.0 and later. |
| PaymentGatewayErrorCode | Type  string  Properties  Create, Filter, Group, Nillable, Sort  Description  The raw error code from the payment gateway for the payment schedule item. Available in API version 66.0 and later. |
| PaymentGatewayRespStatus | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The status of the payment gateway response when the payment schedule item is processed.  Valid values are:  - `Decline` - `Indeterminate` - `PermanentFail` - `RequiresReview` - `Success` - `SystemError` - `ValidationError`  See [SalesforceResultCode Enum](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_enum_commercepayments_SalesforceResultCode.htm) for more information about the values. |
| PaymentId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The payment that a payment run created for the payment schedule item after picking up the parent payment schedule. This field is unique within your organization.  This field is a relationship field.  Relationship Name  Payment  Refers To  Payment |
| PaymentMethodId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The payment method assigned to payments created from the payment schedule item. When a payment schedule item is created, its PaymentMethodId inherits the payment schedule’s DefaultPaymentMethodId. However, you can provide a new PaymentMethodId at any time. If you change the PaymentMethodId, only payments made after the change use the new account.  This field is a polymorphic relationship field.  Relationship Name  PaymentMethod  Refers To  CardPaymentMethod, SavedPaymentMethod |
| PaymentProcessingMessage | Type  string  Properties  Filter, Nillable, Sort  Description  Information about whether the payment creation process has completed. |
| PaymentRetryCount | Type  int  Properties  Create, Filter, Group, Nillable, Sort  Description  The number of payment retries that were attempted on the payment schedule item. Available in API version 66.0 and later. |
| PaymentRunMatchingValue | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The value used to match a payment schedule item to a payment run based on the payment run’s matching criteria. |
| PaymentScheduleId | Type  reference  Properties  Create, Filter, Group, Sort  Description  Required. The parent payment schedule for the payment schedule item.  This field is a relationship field.  Relationship Name  PaymentSchedule  Relationship Type  Master-detail  Refers To  PaymentSchedule (the master object) |
| PaymentScheduleItemNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The auto-generated reference number for the payment schedule item. |
| PaymentSource | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The process that created a payment based on the payment schedule item.  Valid values are:  - `External Payment` - `Payment Run` |
| PaymentsReceived | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The amount that's been received for the payment created for the payment schedule item. |
| ProcessedAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount of the payment schedule item that has been processed for payment and converted to a payment record. |
| RequestedAmount | Type  currency  Properties  Create, Filter, Sort, Update  Description  Required. The initial amount of the payment schedule item upon creation. |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The status of the payment schedule item.  Valid values are:  - `Applied`—The   payment schedule item has been successfully applied. - `Apply Failed`—The   payment run encountered an error when attempting to process   the payment schedule item for payment. For more information,   review the payment run’s revenue transaction error log. - `Canceled`—The   payment schedule item can’t be picked up by payment runs for   processing. When a user or process changes the item’s status   to `Canceled`, the item’s   `CanceledAmount`   becomes `RequestedAmount`   – `ProcessedAmount`. - `Draft`—Payment   schedule items are created with this status. - `Failed`—The   payment run has failed to process the payment schedule item   for payment. - `Processed`—The   payment run has processed the payment schedule item for   payment. - `Processing—`The   payment run is processing the payment schedule item for   payment. - `Ready for   Processing`—The payment schedule item is ready   to be processed by a payment run. |
| TargetPaymentProcessingDate | Type  date  Properties  Create, Filter, Group, Sort, Update  Description  Required. The date when the payment run makes a payment request to the payment gateway for the payment schedule item. |
| UsageType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The feature using the payment schedule item.  Valid value is:  - `CollectionPlan` |
