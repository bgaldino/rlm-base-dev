---
page_id: sforce_api_associated_objects_list.htm
title: Revenue Management Associated Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_associated_objects_list.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Associated Objects
fetched_at: 2026-11-23
---

# Revenue Management Associated Objects

This section provides a list of objects associated to standard objects of Revenue Management
with their standard fields.

Some fields may not be listed for some objects. To see the system fields for each object, see
[System Fields](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/system_fields.htm "HTML (New Window)") in the Object
Reference for Salesforce and Lightning Platform.

To verify the complete list of fields for an object, use a describe call from the API or
inspect with an appropriate tool. For example, inspect the WSDL or use a schema viewer.

- **[StandardObjectNameChangeEvent](./sforce_api_associated_objects_change_event.htm.md)**  
  A ChangeEvent object is available for each object that supports Change Data Capture. You can subscribe to a stream of change events using Change Data Capture to receive data tied to record changes in Salesforce. Changes include record creation, updates to an existing record, deletion of a record, and undeletion of a record. A change event isn’t a Salesforce object—it doesn’t support CRUD operations or queries. It’s included in the object reference so you can discover which Salesforce objects support change events.
- **[StandardObjectNameFeed](./sforce_api_associated_objects_feed.htm.md)**  
  StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.
- **[StandardObjectNameHistory](./sforce_api_associated_objects_history.htm.md)**  
  StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.
- **[StandardObjectNameOwnerSharingRule](./sforce_api_associated_objects_ownersharingrule.htm.md)**  
  StandardObjectNameOwnerSharingRule is the model for all owner sharing rule objects associated with standard objects. These objects represent a rule for sharing a standard object with users other than the owner.
- **[StandardObjectNameShare](./sforce_api_associated_objects_share.htm.md)**  
  StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.
- **[Event](./sforce_api_objects_event.htm.md)**  
  Represents an event in the calendar. In the user interface, event and task records are collectively referred to as activities.
- **[Task](./sforce_api_objects_task.htm.md)**  
  Represents a business activity such as making a phone call or other to-do items. In the user interface, Task and Event records are collectively referred to as activities.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_associated_objects_list.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
