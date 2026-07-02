---
page_id: sforce_api_objects_paymentschedule.htm
title: PaymentSchedule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentschedule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PaymentSchedule

Represents information about a set of payments that a customer wants
to collect at different times for a certain record. A schedule contains one or more payment
schedule items, where each item represents one payment to be processed. Each of a
schedule’s items can have different payment configuration fields, such as payment methods,
payment dates, and payment accounts. When a payment scheduler launches a payment run, the
run evaluates active payment schedule items, and picks them up for payment processing if
they match the scheduler’s payment criteria. This object is available in API version
64.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`undelete()`,
`update()`,
`upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Payment Admin permission set or the
Payment Operations User permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| AvailableRequestedAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The payment schedule’s remaining amount available for the creation of payment schedule items. This value is calculated by deducting the TotalLineRequestedAmount value from the TotalRequestedAmount value.  This field is a calculated field. |
| CollectionPlanItemId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The collection plan item for the payment schedule that’s related to an invoice.  This field is a relationship field.  Relationship Name  CollectionPlanItem  Refers To  CollectionPlanItem |
| Comments | Type  textarea  Properties  Create, Filter, Nillable, Sort, Update  Description  Additional details about the payment schedule. |
| DefaultPaymentAccountId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  When a payment run creates payments from a payment schedule item, it sets the payment’s account to the item’s PaymentAccountId value. When the payment schedule item is created, the item’s PaymentAccountId inherits the schedule’s DefaultPaymentAccountId. However, you can override the PaymentAccountId with a different account as needed. If you do, future payments made from the item use the new account.  This field is a relationship field.  Relationship Name  DefaultPaymentAccount  Refers To  Account |
| DefaultPaymentMethodId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  When a payment run creates payments from a payment schedule item, it sets the payment’s payment method to the item’s PaymentMethodId. When the payment schedule item is created, the item’s PaymentMethodId inherits the schedule’s DefaultPaymentMethodId. However, you can override the PaymentMethodId with a different method as needed. If you do, future payments made from the item will use the new method.  This field is a polymorphic relationship field.  Relationship Name  DefaultPaymentMethod  Refers To  CardPaymentMethod, SavedPaymentMethod |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, and LastReferenceDate is not null, the user accessed this record or list view indirectly. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. The ID of the owner of the Payment Schedule record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| PaymentScheduleNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The auto-generated reference number for the payment schedule. |
| PaymentSource | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description |
| ReferenceEntityId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The object record that receives payments as a result of the related payment schedule items that are processed.  This field is a polymorphic relationship field.  Relationship Name  ReferenceEntity  Refers To  CollectionPlan, Contract, Invoice, Order, Quote |
| RemainingAmountToBeProcessed | Type  currency  Properties  Filter, Nillable, Sort  Description  The total pending amount of payment schedule items that haven’t yet been processed for payment. This value is calculated by deducting the TotalProcessedAmount value from the TotalLineRequestedAmount value.  This field is a calculated field. |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The status of the payment schedule.  Valid values are:  - `Canceled`—Payment   runs can’t evaluate payment schedules or use them to create   payments. - `Completed—`All of   the payment schedule’s payment schedule items have been   processed for payments. - `Draft`—The   payment schedule can be edited and configured. Payment runs   don’t evaluate draft payment schedules. - `Open`—The payment   schedule is available for payment run evaluation. |
| TotalAppliedAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount of all the related payment schedule items that have been applied to payments.  This field is a calculated field. |
| TotalCanceledAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of all RequestedAmount values of all the related payment schedule items with a status of `Canceled`.  This field is a calculated field. |
| TotalPaymentScheduleItemAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The total amount allocated from the payment schedule to its payment schedule items. This value is calculated by deducting the sum of each payment schedule item’s CanceledAmount from the sum of each payment schedule item’s RequestedAmount.  This field is a calculated field. |
| TotalPaymentsReceived | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of all the total payment received for all the related payment schedule items.  This field is a calculated field. |
| TotalProcessedAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of ProcessedAmount values of all the related payment schedule items with a status of `Processed`.  This field is a calculated field. |
| TotalRequestedAmount | Type  currency  Properties  Create, Filter, Sort, Update  Description  Required. The total amount available for a payment schedule to distribute to its payment schedule items. The sum of payment schedule items can’t be greater than the TotalLineRequestedAmount value of the parent payment schedule. |
| UsageType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The feature using the payment schedule.  Valid value is:  - `CollectionPlan` |
