---
page_id: discovery_framework_metadata_api_parent.htm
title: Discovery Framework Metadata API Types
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/discovery_framework_metadata_api_parent.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework.htm
fetched_at: 2026-06-25
---

# Discovery Framework Metadata API Types

Metadata API enables you to access some types and feature settings that you can
customize in the user interface.

For more information about Metadata API and to find a complete reference of existing
metadata types, see **[Metadata API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/)**.

- **[AssessmentQuestion](./meta_assessmentquestion.htm.md)**  
  Represents the container object that stores the questions required for an assessment.
- **[AssessmentQuestionSet](./meta_assessmentquestionset.htm.md)**  
  Represents the container object for Assessment Questions.
- **[DocumentCategory](./meta_documentcategory.htm.md)**  
  Represents a document category.
- **[DocumentCategoryDocumentType](./meta_documentcategorydocumenttype.htm.md)**  
  Represents the junction between a DocumentCategory and a DocumentType. Puts a DocumentType in a DocumentCategory.
- **[DocumentType](./meta_documenttype.htm.md)**  
  Represents a document type.
- **[OmniScript](./meta_omniscript.htm.md)**  
  Represents an OmniScript for the Discovery Framework, which guides users through sales, service, and other business processes. For Discovery Framework, the customization type is `discoveryframework`.
- **[Supported Metadata Channels](./discovery_framework_channels.htm.md)**  
  In Discovery Framework, you can create questions and question sets to categorize questions, and you can move such a dataset across multiple orgs. A metadata wrapper is automatically created for these objects.
- **[Flow for Discovery Framework](./discovery_framework_flow_metadata_api.htm.md)**  
  Represents the metadata associated with a flow. With Flow, you can create an application that navigates users through a series of screens to query and update records in the database. You can also execute logic and provide branching capability based on user input to build dynamic applications.
