---
page_id: deployment_create_guid_field.htm
title: Create a GUID Field
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_create_guid_field.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Deployment
parent_page: deployment_global_UID_setup.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Create a GUID Field

Add a GUID field to all objects used during your deployment to ensure unique
  identification of records across environments.

  
   
1. 
    From Setup, in the Quick Find box, find and select **Object
     Manager**.
   

   
2. 
    Select an object.
   

   
3. 
    Click **Fields & Relationships**.
   

   
4. 
    Click **New**.
   

   
5. 
    Select **Text** for the data type.
   

   
6. 
    Enter a field label and field name.
   

   
7. 
    Enter a length.
    We recommend 255 to avoid any errors related to ID length.
   

   
8. 
    Select **Unique** and **External ID**.
    
     

#### Important

Selecting these attributes ensures that every record gets a unique
      ID.

    
   

   
9. 
    Click **Next**.
   

   
10. 
    Select the appropriate profiles for field access, optionally add the field to page layouts,
     and then click **Save**.
   

   
11. 
    Repeat this process for all Salesforce objects related to your deployment plan.
   

  

  
   

#### Note

Alternatively, you can create GUID fields by using the Metadata API. For more
    information, see [Understanding Metadata API](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_intro.htm) and the
     [Custom Field](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/customfield.htm) metadata type.
