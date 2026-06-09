---
page_id: sforce_api_associated_objects_change_event.htm
title: StandardObjectNameChangeEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_associated_objects_change_event.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Associated Objects
parent_page: sforce_api_associated_objects_list.htm
fetched_at: 2026-06-09
---

# StandardObjectNameChangeEvent

A ChangeEvent object is available for each object that supports Change Data Capture.
You can subscribe to a stream of change events using Change Data Capture to receive data tied to
record changes in Salesforce. Changes include record creation, updates to an existing record,
deletion of a record, and undeletion of a record. A change event isn’t a Salesforce
object—it doesn’t support CRUD operations or queries. It’s included in the object
reference so you can discover which Salesforce objects support change events.

## Supported Calls

`describeSObjects()`

## Special Access Rules

- All objects may not be available in your org. Some objects require specific feature
  settings and permissions to be enabled.
- For more special access rules, if any, see the documentation for the standard object.
  For example, for AccountChangeEvent, see the special access rules for Account.

## Change Event Support

Change events are available for all custom objects and a subset of standard objects. Change
events that correspond to custom settings are partially supported. They aren't supported in
Apex triggers but are supported in other types of subscribers. For more information about
standard object support, see the Objects That Support Change Events section below.

## Change Event Name

The name of a change event is based on the name of the corresponding object for which it
captures the changes.

Standard Object Change Event Name
:   ```
    <Standard_Object_Name>ChangeEvent
    ```
:   Example: `AccountChangeEvent`

Custom Object Change Event Name
:   ```
    <Custom_Object_Name>__ChangeEvent
    ```
:   Example: `MyCustomObject__ChangeEvent`

## Change Event Fields

The fields that a change event can include correspond to the fields on the associated
parent Salesforce object, with a few exceptions. For example, AccountChangeEvent fields
correspond to the fields on Account.

The fields that a change event doesn’t include are:

- The IsDeleted system field.
- The SystemModStamp system field.
- Any field whose value isn’t on the record and is derived from another record or from a
  formula, except roll-up summary fields, which are included. Examples are formula fields.
  Examples of fields with derived values include LastActivityDate and
  PhotoUrl.

Each change event also contains header fields. The header fields are included inside the
`ChangeEventHeader` field. They contain information
about the event, such as whether the change was an update or delete and the name of the
object, like Account.

In addition to the event payload, the event schema ID is included in the
schema field. Also included is the event-specific field,
replayId, which is used for retrieving past events.

## Event Message Example

This example is an event message in JSON format for a new account record creation.

```
{
  "schema": "IeRuaY6cbI_HsV8Rv1Mc5g", 
  "payload": {
    "ChangeEventHeader": {
      "entityName": "Account", 
      "recordIds": [
        "<record_ID>"
      ], 
      "changeType": "CREATE", 
      "changeOrigin": "com/salesforce/api/soap/51.0;client=SfdcInternalAPI/", 
      "transactionKey": "0002343d-9d90-e395-ed20-cf416ba652ad", 
      "sequenceNumber": 1, 
      "commitTimestamp": 1612912679000, 
      "commitNumber": 10716283339728, 
      "commitUser": "<User_ID>"
    }, 
    "Name": "Acme", 
    "Description": "Everyone is talking about the cloud. But what does it mean?", 
    "OwnerId": "<Owner_ID>", 
    "CreatedDate": "2021-02-09T23:17:59Z", 
    "CreatedById": "<User_ID>", 
    "LastModifiedDate": "2021-02-09T23:17:59Z", 
    "LastModifiedById": "<User_ID>"
  }, 
  "event": {
    "replayId": 6
  }
}
```

## API Version and Schema

When you subscribe to change events, the subscription uses the latest API version and the
event messages received reflect the latest field definitions. For more information, see
[API Version and Event Schema](https://developer.salesforce.com/docs/atlas.en-us.262.0.change_data_capture.meta/change_data_capture/cdc_message_structure.htm#cdc_event_schema.htm) in
the Change Data Capture Developer Guide.

## Usage

For more information about Change Data Capture, see [Change Data Capture Developer
Guide](https://developer.salesforce.com/docs/atlas.en-us.262.0.change_data_capture.meta/change_data_capture/cdc_intro.htm).
