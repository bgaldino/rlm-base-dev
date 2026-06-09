---
page_id: deployment_create_guid_field.htm
title: Create a GUID Field
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_create_guid_field.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_global_UID_setup.htm
fetched_at: 2026-06-09
---

# Create a GUID Field

Add a GUID field to all objects used during your deployment to ensure unique
identification of records across environments.

1. From Setup, in the Quick Find box, find and select **Object
   Manager**.
2. Select an object.
3. Click **Fields & Relationships**.
4. Click **New**.
5. Select **Text** for the data type.
6. Enter a field label and field name.
7. Enter a length.

   We recommend 255 to avoid any errors related to ID length.
8. Select **Unique** and **External ID**.

   ![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

   #### Important

   Selecting these attributes ensures that every record gets a unique
   ID.
9. Click **Next**.
10. Select the appropriate profiles for field access, optionally add the field to page layouts,
    and then click **Save**.
11. Repeat this process for all Salesforce objects related to your deployment plan.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

Alternatively, you can create GUID fields by using the Metadata API. For more
information, see [Understanding Metadata API](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_intro.htm "HTML (New Window)") and the
[Custom Field](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/customfield.htm "HTML (New Window)") metadata type.
