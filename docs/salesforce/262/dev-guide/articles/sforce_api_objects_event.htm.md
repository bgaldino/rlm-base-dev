---
page_id: sforce_api_objects_event.htm
title: Event
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_event.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Associated Objects
parent_page: sforce_api_associated_objects_list.htm
fetched_at: 2026-06-09
---

# Event

Represents an event in the calendar. In the user interface, event and
task records are collectively referred to as activities.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

- An EventRelation object can’t be related to a child event, and child
  events don’t include the invitee related list.
- `query()`, `delete()`, and `update()`
  aren’t allowed with events related to more than one contact in API
  versions 25.0 and earlier.
- `create()` and `update()` aren’t available for read-only
  fields on Lightning Experience event series.
- `upsert()` and `undelete()` aren’t supported for syncing
  changes made to events through the API using the feature Lightning
  Sync.

## Supported Calls

`create()`, `delete()`, `describeLayout()`,
`describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| AcceptedEventInviteeIds | Type  JunctionIdList  Properties  Create, Update  Description  A string array of contact or lead IDs who accepted this event. This JunctionIdList is linked to the AcceptedEventRelation child relationship. Warning Warning Adding a JunctionIdList field name to the fieldsToNull property deletes all related junction records. This action can’t be undone. |
| AccountId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  Represents the ID of the related account. The AccountId is determined as follows. If the value of WhatId is any of the following objects, then Salesforce uses that object’s AccountId.   - Account - Opportunity - Contract - Custom object that’s a child of Account   If the value of the WhatId field is any other object, and the value of the WhoId field is a contact object, then Salesforce uses that contact’s AccountId. If your org uses Shared Activities, Salesforce uses the AccountId of the primary contact.  Otherwise, Salesforce sets the value of the AccountId field to `null`.  This is a relationship field.  Relationship Name  Account  Relationship Type  Lookup  Refers To  Account |
| ActivityDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Contains the event’s due date if the IsAllDayEvent flag is set to `true`. This field is a date field with a timestamp that’s always set to midnight in the Coordinated Universal Time (UTC) time zone. Don’t attempt to alter the timestamp to account for time zone differences. Label is **Due Date Only**. This field is required in API versions 12.0 and earlier if the IsAllDayEvent flag is set to `true`.  The value for this field and StartDateTime must match, or one of them must be `null`. |
| ActivityDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  Contains the event’s due date if the IsAllDayEvent flag is set to `false`. The time portion of this field is always transferred in the Coordinated Universal Time (UTC) time zone. Translate the time portion to or from a local time zone for the user or the application, as appropriate. Label is **Due Date Time**. This field is required in API versions 12.0 and earlier if the IsAllDayEvent flag is set to `false`.  The value for this field and StartDateTime must match, or one of them must be `null`. |
| ClientGuid | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The client globally unique identifier identifies the external API client used to create the event. Label is **Client GUID**. |
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Available only for orgs with the multicurrency feature enabled. Contains the ISO code for any currency allowed by the organization. |
| DeclinedEventInviteeIds | Type  JunctionIdLIst  Properties  Create, Update  Description  A string array of contact, lead, or user IDs who declined this event. This JunctionIdList is linked to the DeclinedEventRelation child relationship. Warning Warning Adding a JunctionIdList field name to the fieldsToNull property deletes all related junction records. This action can’t be undone. |
| Description | Type  textarea  Properties  Create, Nillable, Update  Description  Contains a text description of the event. Limit: 32,000 characters. |
| Division | Type  picklist  Properties  Defaulted on create, Filter, Group, Restricted picklist, Sort  Description  A logical segment of your organization's data. For example, if your company is organized into different business units, you could create a division for each business unit, such as “North America,” “Healthcare,” or “Consulting.” Available only if the organization has the Division permission enabled. |
| DurationInMinutes | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Contains the event length, in minutes. Even though this field represents a temporal value, it’s an integer type—not a Date/Time type. Required in API versions 12.0 and earlier if IsAllDayEvent is false.  In API versions 13.0 and later, this field is optional, depending on the following:  - If IsAllDayEvent is true,   you can supply a value for either   DurationInMinutes or   EndDateTime. Supplying values   in both fields is allowed if the values add up to   the same amount of time. If both fields are   `null`, the   duration defaults to one day. - If IsAllDayEvent is   false, a value must be supplied for either   DurationInMinutes or   EndDateTime. Supplying values   in both fields is allowed if the values add up to   the same amount of time.  If the multiday event feature is enabled, then API versions 13.0 and later support values greater than 1440 for the DurationInMinutes field. API versions 12.0 and earlier can’t access event objects whose DurationInMinutes is greater than 1440. For more information, see [**Multiday Events**](#MultidayEventsDesc).  Depending on your API version, errors with the DurationInMinutes and EndDateTime fields may appear in different places.  - Versions 38.0 and before—Errors always   appear in the   DurationInMinutes field. - Versions 39.0 and later—If there’s no   value for the   DurationInMinutes field,   errors appear in the   EndDateTime field. Otherwise,   they appear in the   DurationInMinutes field. |
| EndDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  Read-only. Available in API versions 46.0 and later. This field supplies the date value that appears in the EndDateTime field. This field is a date field with a timestamp that is always set to midnight in the Coordinated Universal Time (UTC) time zone. |
| EndDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  Available in API versions 13.0 and later. The time portion of this field is always transferred in the Coordinated Universal Time (UTC) time zone. Translate the time portion to or from a local time zone for the user or the application, as appropriate. This field is optional, depending on the following:   - If IsAllDayEvent is true,   you can supply a value for either   DurationInMinutes or   EndDateTime. Supplying values   in both fields is allowed if the values add up to   the same amount of time. If both fields are   `null`, the   duration defaults to one day. - If IsAllDayEvent is false,   a value must be supplied for either   DurationInMinutes or   EndDateTime. Supplying values   in both fields is allowed if the values add up to   the same amount of time.   Depending on your API version, errors with the DurationInMinutes and EndDateTime fields may appear in different places.  - Versions 38.0 and before—Errors always   appear in the   DurationInMinutes field. - Versions 39.0 and later—If there’s no   value for the   DurationInMinutes field,   errors appear in the   EndDateTime field. Otherwise,   they appear in the   DurationInMinutes field. |
| EventSubtype | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort  Description  Provides standard subtypes to facilitate creating and searching for events. This field isn’t updateable. |
| EventWhoIds | Type  JunctionIdList  Properties  Create, Update  Description  A string array of contact or lead IDs used to create many-to-many relationships with a shared event. EventWhoIds is available when the shared activities setting is enabled. The first contact or lead ID in the list becomes the primary WhoId if you don’t specify a primary WhoId. If you set the EventWhoIds field to null, all entries in the list are deleted and the value of WhoId is added as the first entry. Warning Warning Adding a JunctionIdList field name to the fieldsToNull property deletes all related junction records. This action can’t be undone. |
| GroupEventType | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  Read-only. Available in API versions 19.0 and later. The possible values are:  - `0`   (Non–group event)—An event with no   invitees. - `1` (Group   event)—An event with invitees. - `2`   (Proposed event)—An event created when a   user requests a meeting with a contact, lead, or   person account using the Salesforce user   interface. When the user confirms the meeting, the   proposed event becomes a group event. You   can’t create, edit, or delete proposed   events in the API. This value is no longer used in   API version 41.0 and later. - `3`   (IsRecurrence2 Series Pattern)—An event   representing an event series recurrence pattern in   Lightning Experience. |
| IsAllDayEvent | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the ActivityDate field (`true`) or the ActivityDateTime field (`false`) is used to define the date or time of the event. Label is **All-Day Event**. See also [DurationInMinutes](#DurationInMinutesField) and [EndDateTime](#EndDateTimeField). |
| IsArchived | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the event has been archived. |
| IsChild | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the event is a child of another event (`true`) or not (`false`).  For a child event, you can update IsReminderSet and ReminderDateTime only. You can query and delete a child event. If the objects related to the child event are different from those objects related to the parent event (this difference is possible if you use API version 25.0 or earlier) and one of the objects related to the child event is deleted, the objects related to the parent event are updated to ensure data integrity. |
| IsClientManaged | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the event is managed by an external client. If the value of this field is false, the event isn’t owned or managed by an external client, and Salesforce can be used to update it. If the value is true, Salesforce can be used to change only noncritical fields on the event. Label is **Is Client Managed**. |
| IsGroupEvent | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the event is a group event—that is, whether it has invitees (`true`) or not (`false`). |
| IsPrivate | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether users other than the creator of the event can (`false`) or can’t (`true`) see the event details when viewing the event user’s calendar. However, users with the View All Data or Modify All Data permission can see private events in reports and searches, or when viewing other users’ calendars. Private events can’t be associated with opportunities, accounts, cases, campaigns, contracts, leads, or contacts. Label is **Private**. |
| IsRecurrence | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort  Description  Indicates whether a Salesforce Classic event is scheduled to repeat itself (`true`) or only occurs one time (`false`). This field is read-only when updating records, but not when creating them. If this field value is `true`, then RecurrenceEndDateOnly, RecurrenceStartDateTime, RecurrenceType, and any recurrence fields associated with the given recurrence type must be populated. Label is **Create recurring series of events**. |
| IsRecurrence2 | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Read-only. This field is available in API version 44.0 and later. Indicates whether a Lightning Experience event is scheduled to repeat (`true`) or only occurs one time (`false)`. If this field value is true, then Recurrence2PatternText and Recurrence2PatternVersion must be populated. Label is **Repeat**. |
| IsRecurrence2Exception | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Read-only. This field is available in API version 44.0 and later. Indicates whether an individual event in a Lightning Experience event series has a recurrence pattern that’s different from the rest of the series, making it an exception. |
| IsRecurrence2Exclusion | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Read-only. This field is available in API version 44.0 and later. Indicates when updates to a Lightning Experience event series recurrence pattern have been made, but affect future event occurrences only. For past event occurrences, IsRecurrence2Exclusion is set to `true`, excluding past occurrences from the series recurrence pattern. |
| IsReminderSet | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the activity is a reminder (`true`) or not (`false`). |
| IsVisibleInSelfService | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether an event associated with an object can be viewed in the Customer Portal (`true`) or not (`false`). If your org has enabled digital experiences, events marked IsVisibleInSelfService are visible to any external user in the Experience Cloud site, as long as the user has access to the record the event was created on. This field is available when  - Customer Portal or partner portal is   enabled  OR  - Digital experiences is enabled and you have   Customer Portal or partner portal licenses |
| Location | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Contains the location of the event. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Contains the ID of the user or public calendar who owns the event. Label is **Assigned to ID**.  This is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Calendar, User |
| Recurrence2PatternStartDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Read-only. This field is available in API version 44.0 and later. Indicates the date and time when the Lightning Experience event series begins. The time portion of this field is always transferred in the Coordinated Universal Time (UTC) time zone. Translate the time portion to or from a local time zone for the user or the application, as appropriate. |
| Recurrence2PatternText | Type  textarea  Properties  Create, Nillable  Description  The RRULE that describes the recurrence pattern for Lightning Experience event series. Supports a subset of the RFC 5545 standard for internet calendaring and scheduling. See the Event Series section in this topic for usage examples. This field has a maximum length of 512 characters. This field is available in API version 44.0 and later, and has the Create property in API version 52.0 and later. |
| Recurrence2PatternTimeZone | Type  string  Properties  Filter, Group, Nillable, Sort  Description  This field is available in API version 44.0 and later. Indicates the time zone in which the Lightning Experience event series was created or updated. This field uses standard Java TimeZone IDs. For example, America/Los\_Angeles. |
| Recurrence2PatternVersion | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort,  Description  Read-only. This field is available in API version 44.0 and later. Indicates the standard specifications for Lightning Experience event series recurrence patterns. The only possible value is `1` (RFC 5545 v4 RRULE)—RFC 5545 is a standard set of specifications for internet calendaring and scheduling that IsRecurrence2 adheres to for series recurrence patterns. RFC 5545 specifications for series recurrence patterns are called RRULES. For examples of RRULE usage, see the Lightning Experience Event Series and Recurring Events section in this topic. |
| RecurrenceActivityId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  Read-only. Not required on create. Contains the ID of the main record of the Salesforce Classic recurring event. Subsequent occurrences have the same value in this field. |
| RecurrenceDayOfMonth | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Indicates the day of the month on which the event repeats. |
| RecurrenceDayOfWeekMask | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Indicates the day or days of the week on which the Salesforce Classic recurring event repeats. This field contains a bitmask. The values are as follows:  - Sunday = `1` - Monday = `2` - Tuesday = `4` - Wednesday = `8` - Thursday = `16` - Friday = `32` - Saturday = `64`  Multiple days are represented as the sum of their numerical values. For example, Tuesday and Thursday = 4 + 16 = 20. |
| RecurrenceEndDateOnly | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Indicates the last date on which the event repeats. For multiday Salesforce Classic recurring events, this date is the day on which the last occurrence starts. This field is a date field with a timestamp that is always set to midnight in the Coordinated Universal Time (UTC) time zone. Don’t attempt to alter the timestamp to account for time zone differences. |
| RecurrenceInstance | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Indicates the frequency of the Salesforce Classic event’s recurrence. For example, `2nd` or `3rd`. |
| RecurrenceInterval | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Indicates the interval between Salesforce Classic recurring events. |
| RecurrenceMonthOfYear | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Indicates the month in which the Salesforce Classic recurring event repeats. |
| RecurrenceStartDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  Indicates the date and time when the Salesforce Classic recurring event begins. The value must precede the RecurrenceEndDateOnly. The time portion of this field is always transferred in the Coordinated Universal Time (UTC) time zone. Translate the time portion to or from a local time zone for the user or the application, as appropriate. |
| RecurrenceTimeZoneSidKey | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Indicates the time zone associated with a Salesforce Classic recurring event. For example, “UTC-8:00” for Pacific Standard Time. |
| RecurrenceType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Indicates how often the Salesforce Classic event repeats. For example, daily, weekly, or every nth month (where “nth” is defined in RecurrenceInstance). |
| ReminderDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  Represents the time when the reminder is scheduled to fire, if IsReminderSet is set to `true`. If IsReminderSet is set to `false`, then the user may have deselected the reminder checkbox in the Salesforce user interface, or the reminder has already fired at the time indicated by the value. |
| ShowAs | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Indicates how this event appears when another user views the calendar: Busy, Out of Office, or Free. Label is **Show Time As**. |
| StartDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  Indicates the start date and time of the event. Available in versions 13.0 and later. If the Event IsAllDayEvent flag is set to true (indicating that it’s an all-day Event), then the event start date information is contained in the StartDateTime field. The time portion of this field is always transferred in the Coordinated Universal Time (UTC) time zone. Translate the time portion to or from a local time zone for the user or the application, as appropriate.  If the Event IsAllDayEvent flag is set to false (indicating that it isn’t an all-day event), then the event start date information is contained in the StartDateTime field. The time portion is always transferred in the Coordinated Universal Time (UTC) time zone. You need to translate the time portion to or from a local time zone for the user or the application, as appropriate.  If this field has a value, then ActivityDate and ActivityDateTime must either be `null` or match the value of this field. |
| Subject | Type  combobox  Properties  Create, Filter, Nillable, Sort, Update  Description  The subject line of the event, such as Call, Email, or Meeting. Limit: 255 characters. |
| Type | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Indicates the event type, such as Call, Email, or Meeting. |
| UndecidedEventInviteeIds | Type  JunctionIdList  Properties  Create, Update  Description  A string array of contact, lead, or user IDs who are undecided about this event. This JunctionIdList is linked to the UndecidedEventRelation child relationship. Warning Warning Adding a JunctionIdList field name to the fieldsToNull property deletes all related junction records. This action can’t be undone. |
| WhatCount | Type  int  Properties  Filter, Group, Nillable, Sort  Description  Available if your organization has enabled Shared Activities. Represents the count of related EventRelations pertaining to the WhatId. The count of the WhatId must be `1` or less. |
| WhatId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The WhatId represents nonhuman objects such as accounts, opportunities, campaigns, cases, or custom objects. WhatIds are polymorphic. Polymorphic means a WhatId is equivalent to the ID of a related object. The label is Related To ID.  This is a polymorphic relationship field.  Relationship Name  What  Relationship Type  Lookup  Refers To  Account, Accreditation, AssessmentIndicatorDefinition, AssessmentTask, AssessmentTaskContentDocument, AssessmentTaskDefinition, AssessmentTaskOrder, Asset, AssetRelationship, AssignedResource, Award, BoardCertification, BusinessLicense, BusinessMilestone, BusinessProfile, Campaign, CareBarrier, CareBarrierDeterminant, CareBarrierType, CareDeterminant, CareDeterminantType, CareDiagnosis, CareInterventionType, CareMetricTarget, CareObservation, CareObservationComponent, CarePgmProvHealthcareProvider, CarePreauth, CarePreauthItem, CareProgram, CareProgramCampaign, CareProgramEligibilityRule, CareProgramEnrollee, CareProgramEnrolleeProduct, CareProgramEnrollmentCard, CareProgramGoal, CareProgramProduct, CareProgramProvider, CareProgramTeamMember, CareProviderAdverseAction, CareProviderFacilitySpecialty, CareProviderSearchableField, CareRegisteredDevice, CareRequest, CareRequestDrug, CareRequestExtension, CareRequestItem, CareSpecialty, CareSpecialtyTaxonomy, CareTaxonomy, Case, CommSubscriptionConsent, ContactEncounter, ContactEncounterParticipant, ContactRequest, Contract, CoverageBenefit, CoverageBenefitItem, CreditMemo, DelegatedAccount, DocumentChecklistItem, EnrollmentEligibilityCriteria, HealthcareFacility, HealthcareFacilityNetwork, HealthcarePayerNetwork, HealthcarePractitionerFacility, HealthcareProvider, HealthcareProviderNpi, HealthcareProviderSpecialty, HealthcareProviderTaxonomy, IdentityDocument, Image, IndividualApplication, Invoice, ListEmail, Location, MemberPlan, Opportunity, Order, OtherComponentTask, PartyConsent, PersonLifeEvent, PlanBenefit, PlanBenefitItem, ProcessException, Product2, ProductItem, ProductRequest, ProductRequestLineItem, ProductTransfer, PurchaserPlan, ReceivedDocument, ResourceAbsence, ReturnOrder, ReturnOrderLineItem, ServiceAppointment, ServiceResource, Shift, Shipment, ShipmentItem, Solution, Visit, VisitedParty, VolunteerProject, WorkOrder, WorkOrderLineItem |
| WhoCount | Type  int  Properties  Filter, Group, Nillable, Sort  Description  Available to organizations that have Shared Activities enabled. Represents the count of related EventRelations pertaining to the WhoId. |
| WhoId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The WhoId represents a human such as a lead or a contact. WhoIds are polymorphic. Polymorphic means a WhoId is equivalent to a contact’s ID or a lead’s ID. The label is Name ID. If Shared Activities is enabled, the value of this field is the ID of the related lead or primary contact. If you add, update, or remove the WhoId field, you might encounter problems with triggers, workflows, and data validation rules that are associated with the record. The label is Name ID.  If the JunctionIdList field is used, all WhoIds are included in the relationship list.  Beginning in API version 37.0, if the contact or lead ID in the WhoId field isn't in the EventWhoIds list, no error occurs and the ID is added to the EventWhoIds as the primary WhoId. If WhoId is set to null, an arbitrary ID from the existing EventWhoIds list is promoted to the primary position.  This is a polymorphic relationship field.  Relationship Name  Who  Relationship Type  Lookup  Refers To  Contact, Lead |

## Usage

Use Event to manage calendar appointments.

Queries on events are denied before they time out if they involve amounts of data
that are deemed too large. In such cases, the exception code `OPERATION_TOO_LARGE` is returned. If you receive
`OPERATION_TOO_LARGE`, refactor your query to
return or scan a smaller amount of data.

When querying for events with a specific due date, you must filter on both the
ActivityDateTimeand and ActivityDate
fields. For example to find all events with a due date of February 14, 2003, you
need two filters:

- One filter with the ActivityDate field equal to the
  Coordinated Universal Time (UTC) time zone on February 14, 2003.
- One filter with the ActivityDate field greater than or
  equal to midnight on February 14, 2003 in the user’s local time zone
  AND less than or equal to midnight on February 15, 2003 in the user’s
  local time zone.

Alternatively, in API version 13.0 and later, you can find events with a specific due date by
filtering on StartDateTime. For example, to find all events
with a due date of February 14, 2003, filter with the
StartDateTime greater than or equal to midnight on February
14, 2003 in the user's local time zone AND less than or equal to midnight on
February 15, 2003 in the user's local time zone.

The EventId field of an EventRelation object always points to
the master record. An invitee on a group event can query the EventRelation object to
view the master record.

**Multiday Events**

- Multiday events are available in API version 13.0 and later. Also, in earlier versions SOQL
  queries don’t return multiday events.
- Multiday events are enabled through the user interface from Setup by
  entering `Activity Settings` in the Quick
  Find box, then selecting **Activity
  Settings**.
- If the multiday event feature is enabled, then API versions 13.0 and later
  support values greater than 1440 for the
  DurationInMinutes field. API versions 12.0 and
  earlier can’t access event objects whose
  DurationInMinutes is greater than 1440.
- Multiday events can’t exceed 14 days.

**Event Series and Recurring Events**

In Lightning Experience, events with multiple occurrences are called event series,
and are indicated when the IsRecurrence2 field is set to
`true`. In Salesforce Classic, events with
multiple occurrences are called recurring events, and are indicated when the
IsRecurrence field is set to `true`. Both fields can’t be set to true for the same event.

- Lightning Experience event series are available in API version 44.0 and later as
  read-only fields. Recurrence patterns, specified by the Recurrence2PatternText
  field, are creatable in API version 52.0 and later. Salesforce Classic recurring
  events are available in API version 7.0 and later. In earlier versions, SOQL
  queries don’t return any Lightning Experience event series.
- After an event is created, you can’t change the values of
  IsRecurrence2 or IsRecurrence from
  `true` to `false` or vice versa.
- You can’t set fields associated with IsRecurrence2 for
  events where IsRecurrence is set to `true`, or vice versa.
- For Lightning Experience event series where IsRecurrence2
  is `true`, if you’d like to delete a single
  or all remaining events, use the REST API call. For Salesforce Classic recurring events where
  IsRecurrence is `true`, all past and future events in the series are removed when
  you delete the recurring event series through the API. However, when you delete
  the recurring event series through the user interface, only future occurrences
  are removed.
- For Lightning Experience event series in API version 58.0 and later, when you
  change a future event, events in the entire series also change. When you change
  a past event, IsRecurrence2Exception is set to `true` and only that past event changes.
- When creating a Salesforce Classic recurring event series, the duration of the
  event must be 24 hours or less. When the Salesforce Classic recurring event
  series is created, you can extend the length of individual occurrences beyond 24
  hours if Multiday events are enabled; see **Multiday Events**.
- For Salesforce Classic recurring events,
  RecurrenceStartDateTime,
  RecurrenceEndDateOnly,
  RecurrenceType, and any properties associated with the
  given recurrence type (see the Recurrence Field Usage for Salesforce Classic
  Recurring Events table) must be populated.
- When updating a Salesforce Classic recurring event series, it’s not
  possible to update the EventRelation for the event series
  object and the EventRelation for the series object occurrences at the same
  time.
- Lightning Experience event series have no series ID, so it’s not possible to
  locate other occurrences in the series. In Salesforce Classic recurring events,
  you can use RecurrenceActivityId to locate other
  occurrences.
- For both Lightning Experience event series and Salesforce Classic recurring
  events, when a series repeats every day, month, or year, you can only schedule
  occurrences one time per day, month, or year. The week option lets you schedule
  occurrences multiple days per week.

[Limits for Lightning Experience event series](https://help.salesforce.com/s/articleView?id=sales.creating_events_lex.htm&type=5&language=en_US "HTML (New Window)") and [limits for Salesforce Classic recurring events](https://help.salesforce.com/s/articleView?id=sales.creating_events_cex.htm&type=5&language=en_US "HTML (New Window)") also apply.

**Lightning Experience Event Series and Recurring Events**

Use the `Recurrence2PatternText` field to specify
the recurrence pattern for Lightning Experience event series. These recurrence
patterns, called reference rules or RRULES, support a subset of the RFC 5545
standards. This table includes common RRULE examples.

| Recurrence Pattern | RRULE Example |
| --- | --- |
| Every day for five days | `RRULE:FREQ=DAILY;INTERVAL=1;COUNT=5` |
| Every Monday, Tuesday, Wednesday, Thursday, and Friday with no end date | `RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,TU,WE,TH,FR` |
| Every two weeks on Monday and Friday for 10 occurrences | `RRULE:FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,FR;COUNT=10` |
| Monthly on the first day of the month until January 1, 2020 | `RRULE:FREQ=MONTHLY;INTERVAL=1;BYMONTHDAY=1;UNTIL=20200101T100000Z` |
| Yearly on July 4th for three years (in this example, specify the date using StartDateTime) | `RRULE:FREQ=YEARLY;INTERVAL=1;BYMONTH=7;BYMONTHDAY=4;COUNT=3` |
| Daily until January 1, 2022 with no end date | `RRULE:FREQ=DAILY;UNTIL=20220101T000000Z` |
| Every third Friday of the month with no end date | `RRULE:FREQ=MONTHLY;BYSETPOS=3;BYDAY=FR` |

The RRULE defined by `Recurrence2PatternText`
supports a subset of the RFC 5545 standard for internet calendaring and scheduling.
Supported RRULE parts include FREQ, BYMONTH, BYMONTHDAY, BYDAY, WKST, BYSETPOS,
INTERVAL, UNTIL, and COUNT.

When the event record is saved, the RRULE might be modified to follow the required format:

- The RRULE parts are placed in the following order: FREQ, BYMONTH,
  BYMONTHDAY, BYDAY, WKST, BYSETPOS, INTERVAL, UNTIL, and COUNT.
- Any missing default values are inserted. For example, if the RRULE doesn't
  include INTERVAL, then `INTERVAL=1` is
  added.
- The RRULE is prefaced with `RRULE:` if
  that preface is missing.

| RRULE Part | Supported RFC 5545 Implementation |
| --- | --- |
| FREQ | Required. Indicates the type of recurrence rule. Allowed values are:  - `DAILY`—supported parts include FREQ,   INTERVAL, UNTIL, and COUNT. - `WEEKLY`—supported parts include   INTERVAL, UNTIL, COUNT, BYDAY, and WKST. BYDAY is   required, but can't be preceded by a number. For   example, to indicate weekly on Tuesday and Thursday   until September 1, 2023, use `RRULE:FREQ=WEEKLY;UNTIL=20230901T000000Z;BYDAY=TU,TH` - `MONTHLY`—supported patterns include:   - BYMONTHDAY For example, to indicate monthly on     the third day of the month use: `RRULE:FREQ=MONTHLY;BYMONTHDAY=3`   - BYDAY and BYSETPOS For example, to indicate     the last weekday of the month, use `RRULE:FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-1`   - BYDAY, where the BYDAY values are specified with     a numeric value For example, to indicate monthly     on the first Friday for 10 occurrences, use     `RRULE:FREQ=MONTHLY;COUNT=10;BYDAY=1FR` - `YEARLY`—supported patterns include:   - BYMONTH, BYDAY, and BYSETPOS For example, to     indicate every year on the second Friday of     January, use `RRULE:FREQ=YEARLY;BYMONTH=1;BYDAY=FR;BYSETPOS=2`   - BYMONTH and BYMONTHDAY For example, to indicate every year on October 31, use     `RRULE:FREQ=YEARLY;BYMONTH=10;BYMONTHDAY=31`  For     example, to create a maintenance pattern such as     twice in May, and September on 7th and 15th; and     one time in June/July/August on the 1st, use two     RRULEs: `RRULE:     FREQ=MONTHLY; BYMONTH=5,9; BYMONTHDAY=7,     15`     `RRULE:FREQ=MONTHLY;     BYMONTH=6,7,8; BYMONTHDAY=1` |
| BYMONTH | The month. Valid values are `1` to `12`. |
| BYMONTHDAY | The day of the month. Valid values are `1` to `31`. If BYMONTHDAY is `31` and the month has fewer than 31 days, the event is created on the last day of the month. |
| BYDAY | A comma-separated list of days of the week. Valid values are `SU`, `MO`, `TU`, `WE`, `TH`, `FR`, `SA`. For RRULES with yearly or monthly frequency, BYDAY must be one of:  - a single day - weekend days - weekdays - every day of the week   Each BYDAY value can be preceded by an integer that indicates the nth occurrence of a specific day within the monthly or yearly RRULE. Allowed values are `-1`, `1`, `2`, `3`, and `4`. You can't use different numbers in the BYDAY values. For example, this RRULE isn’t supported: `RRULE:FREQ=MONTHLY;INTERVAL=2;COUNT=10;BYDAY=1SU,-1SU` If BYDAY values are prefaced with a number, the RRULE can't include BYSETPOS. |
| WKST | Specifies the day on which the workweek starts. Valid values are `MO`, `TU`, `WE`, `TH`, `FR`, `SA`, and `SU`. Default value is based on the user's locale. |
| BYSETPOS | A comma-separated list of values that correspond to the nth occurrence within the set of recurrence instances specified by the rule. Valid values are `-1`, `1`, `2`, `3`, or `4`. Default value is `1`. For example, to indicate the last weekday of the month, use: `RRULE:FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-1` |
| INTERVAL | The repetition interval. Valid values are:  - an integer between `1` and `999` if FREQ=DAILY - an integer between `1` and `99` if FREQ=WEEKLY or FREQ=MONTHLY - `1` if   FREQ=YEARLY  Default value is `1`. |
| UNTIL | Specifies the datetime in UTC format when the recurrence rule stops. The supported format is yyyyMMddTHHmmssZ, for example: 20210419T083000Z. An RRULE can't contain both UNTIL and COUNT. A recurring event without either UNTIL or COUNT repeats indefinitely. |
| COUNT | The number of occurrences. Allowed values are 1 to 999. An RRULE can't contain both UNTIL and COUNT. A recurring event without either UNTIL or COUNT repeats indefinitely. |
| BYWEEKNO | Specifies a comma-separated list of values that specify weeks of the year. Valid values are:  - `1` to `53` - `-53` to `-1`   For example, to indicate specific weeks in a year, use: `RRULE: BYWEEKNO=20, -20`.  This rule part can’t be used when the FREQ rule part is set to anything other than YEARLY. For example, 3 represents the third week of the year.  Note: Assuming a Monday week start, week 53 can only occur when Thursday is January 1 or if it’s a leap year and Wednesday is January 1. |
| BYYEARDAY | Specifies a comma-separated list of values that specify days of the year. Valid values are:  - `1` to `366` - `-366` to `-1`   For example, to indicate specific days in a year, use: `RRULE:BYYEARDAY=1,100,200`; or, `RRULE:BYYEARDAY=1,-2`. |

**Salesforce Classic Event Series and Recurring Events**

This table describes the usage of recurrence fields for
Salesforce Classic recurring events. Each recurrence type must have all of its
properties set. All unused properties must be set to null.

| RecurrenceType Value | Properties | Example Pattern |
| --- | --- | --- |
| RecursDaily | RecurrenceInterval | Every second day |
| RecursEveryWeekday | RecurrenceDayOfWeekMask | Every weekday - can’t be Saturday or Sunday |
| RecursMonthly | RecurrenceDayOfMonth RecurrenceInterval | Every second month, on the third day of the month |
| RecursMonthlyNth | RecurrenceInterval RecurrenceInstance RecurrenceDayOfWeekMask | Every second month, on the last Friday of the month |
| RecursWeekly | RecurrenceInterval RecurrenceDayOfWeekMask | Every three weeks on Wednesday and Friday |
| RecursYearly | RecurrenceDayOfMonth RecurrenceMonthOfYear | Every March on the 26th day of the month |
| RecursYearlyNth | RecurrenceDayOfWeekMask RecurrenceInstanceRecurrenceMonthOfYear | The first Saturday in every October |

**Attendees, Invitees, and
Resources**

The field GroupEventType indicates that event participants are
included on an event. You can add a resource to an event only
when the resource is available. The only attendance status that can be assigned
to resources is Accepted. Events can’t be saved when resources you’ve added
aren’t available.

**JunctionIdList**

To create an event using JunctionIdList, IDs are pulled from the
related contacts and both the event and the EventRelation
records are created in one API call. If the EventRelation
fails, the event is rolled back because it’s all done in a single API
call.

```
public void createEventNew(Contact[] contacts) {
	String[] contactIds = new String[contacts.size()];
	for (int i = 0; i < contacts.size(); i++) {
		contactIds[i] = contacts[i].getID();
	}
	Event event = new Event();
	event.setSubject("New Event");
	event.setEventWhoIds(contactIds);
	SaveResult[] results = null;
	try {
		results = connection.create(new Event[] {
			task
		});
	} catch (ConnectionException ce) {
		ce.printStackTrace();
	}
}
```

**Syncing Events with Lightning Sync**

Attendee statuses (Accepted or Maybe, Declined, or No Response)
sync from Microsoft® Exchange or Google to Salesforce, but not from Salesforce
to Exchange or Google. Be wary of creating API flows that update attendee status
in Salesforce for users set up to sync both ways. Eventually the original
Exchange or Google status overrides the update made in Salesforce.

**Shared Field-Level Security for Event and Task
Objects**

Metadata deployments for the Event object must include the field-level
security for the Task object. Shared field-level security prevents each object
from changing the field-level security of the associated object.

Metadata deployments that include field-level security for only one of either the
Event or Task objects can cause field-level security changes to the other object
that aren't reflected in the metadata.

- If field-level security is enabled for one object, then field-level security is
  enabled for both objects.
- If field-level security is disabled for one object, then it's disabled for both
  objects.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

A missing entry in the metadata is treated as field-level security being
disabled.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re
available in the specified API version and later.

[EventChangeEvent](./sforce_api_associated_objects_change_event.htm.md "A ChangeEvent object is available for each object that supports Change Data Capture. You can subscribe to a stream of change events using Change Data Capture to receive data tied to record changes in Salesforce. Changes include record creation, updates to an existing record, deletion of a record, and undeletion of a record. A change event isn’t a Salesforce object—it doesn’t support CRUD operations or queries. It’s included in the object reference so you can discover which Salesforce objects support change events.") (API version 44.0)
:   Change events are available for the object.

[EventFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.") (API version 20.0)
:   Feed tracking is available for the object.
