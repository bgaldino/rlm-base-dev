---
page_id: apex_class_ind_docgen_api_EnvelopeStatusScheduler.htm
title: EnvelopeStatusScheduler Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/apex_class_ind_docgen_api_EnvelopeStatusScheduler.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: apex_namespace_ind_docgen_api.htm
fetched_at: 2026-10-13
---

# EnvelopeStatusScheduler Class

The `ind_docgen_api.EnvelopeStatusScheduler` class
    schedules Envelope Status updates.

## Namespace

[ind_docgen_api](./apex_namespace_ind_docgen_api.htm.md)

## Example

      
      

```
ind_docgen_api.EnvelopeStatusScheduler envelopeScheduler = new ind_docgen_api.EnvelopeStatusScheduler();
System.schedule('Update Docusign Envelope Job 1', '0 0 * * * ?', envelopeScheduler);
System.schedule('Update Docusign Envelope Job 2', '0 15 * * * ?', envelopeScheduler);
System.schedule('Update Docusign Envelope Job 3', '0 30 * * * ?', envelopeScheduler);
System.schedule('Update Docusign Envelope Job 4', '0 45 * * * ?', envelopeScheduler);
```

    

- 
**[EnvelopeStatusScheduler Methods](./apex_class_ind_docgen_api_EnvelopeStatusScheduler.htm.md#apex_ind_docgen_api_EnvelopeStatusScheduler_methods)**  

## EnvelopeStatusScheduler Methods

The following are methods for `EnvelopeStatusScheduler`.

- 
**[execute(ctx)](./apex_class_ind_docgen_api_EnvelopeStatusScheduler.htm.md#apex_ind_docgen_api_EnvelopeStatusScheduler_execute)**  

Executes the scheduled Apex job for Envelope Status     Updates.

  

### execute(ctx)

  
  
  
Executes the scheduled Apex job for Envelope Status
    Updates.

    

#### Signature

      
      

`public void execute(System.SchedulableContext ctx)`

      
    

    

#### Parameters

      
      

**ctx**

      

Type: [System.SchedulableContext](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexref.meta/apexref/apex_interface_system_schedulablecontext.htm)

      

Contains the job ID.

    

    

#### Return Value

      
      

Type: void
