---
page_id: omnistudio_apis.htm
title: Omnistudio Business REST APIs
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/omnistudio_apis.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_overview.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Omnistudio Business REST APIs

Omnistudio Business APIs are RESTful APIs that are sometimes available as Apex classes
    and methods. You can access Omnistudio APIs using REST endpoints. These REST APIs follow similar
    conventions as Connect REST APIs.

    

#### Note

These APIs have been deprecated as of API version 55.0. In API version
        55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

    
      

OmniStudio provides a suite of services, components, and data model objects that combine to
        create Industry Cloud applications. Create guided interactions using data from your
        Salesforce org and external sources.

      

To understand the architecture, authentication, rate limits, and how the requests and
        responses work, see [Connect REST API Developer
          Guide](https://developer.salesforce.com/docs/atlas.en-us.264.0.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm).

    

  

- 
**[Expression Set](./omnistudio_calculation_procedure_apis_resources.htm.md)**  

An expression set allow complex math to be configured within       OmniStudio. Expression set is also known as calculation Procedure or evaluation     service.

- 
**[Decision Matrix](./omnistudio_decision_matrix_apis_resources.htm.md)**  

A decision matrix is a table that looks up information using multiple       input dimensions and returns the corresponding output value. Decision matrix is also known as       calculation matrix.

- 
**[Data Mapper](./omnistudio_data_mapper_apis.htm.md)**  

The Data Mapper is a mapping tool that you use to read, transform, and write Salesforce     data. Omnistudio Data Mapper is time-efficient and easier to maintain for data processing. Data     Mappers typically supply data to Omniscripts, Integration Procedures, Flexcards, and Apex     classes, and write the related updates to Salesforce.

- 
**[Integration Procedure](./omnistudio_integration_procedure_apis.htm.md)**  

Integration procedures can read and write data from Salesforce and external systems by     using the REST API calls and Apex classes. An Integration Procedure can be called from an     Omniscript, an API, or an Apex method, and can be a data source for a Flexcard. Integration     Procedures can handle multiple data sources to read and write data.

#### See Also

- [Omnistudio Foundation Guide](https://volt.my.salesforce.com/sfc/p/o0000000IKm8/a/3m000000nWyq/erXZ51SEaoeirtkzzlQnC5GehNzqvrSTTU3I1rOd3gs)
