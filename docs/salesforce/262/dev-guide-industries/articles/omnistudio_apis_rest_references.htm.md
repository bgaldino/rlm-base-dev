---
page_id: omnistudio_apis_rest_references.htm
title: REST Reference
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/omnistudio_apis_rest_references.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis.htm
fetched_at: 2026-06-25
---

# REST Reference

You can access Omnistudio APIs using REST endpoints. These REST APIs follow similar
conventions as Connect REST APIs.

To understand the architecture, authentication, rate limits, and how the requests and
responses work, see [Connect REST API Developer
Guide](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm "HTML (New Window)").

- **[Expression Set](./omnistudio_calculation_procedure_apis_resources.htm.md)**  
  An expression set allow complex math to be configured within OmniStudio. Expression set is also known as calculation Procedure or evaluation service.
- **[Decision Matrix](./omnistudio_decision_matrix_apis_resources.htm.md)**  
  A decision matrix is a table that looks up information using multiple input dimensions and returns the corresponding output value. Decision matrix is also known as calculation matrix.
- **[Data Mapper](./omnistudio_data_mapper_apis.htm.md)**  
  The Data Mapper is a mapping tool that you use to read, transform, and write Salesforce data. Omnistudio Data Mapper is time-efficient and easier to maintain for data processing. Data Mappers typically supply data to Omniscripts, Integration Procedures, Flexcards, and Apex classes, and write the related updates to Salesforce.
- **[Integration Procedure](./omnistudio_integration_procedure_apis.htm.md)**  
  Integration procedures can read and write data from Salesforce and external systems by using the REST API calls and Apex classes. An Integration Procedure can be called from an Omniscript, an API, or an Apex method, and can be a data source for a Flexcard. Integration Procedures can handle multiple data sources to read and write data.
