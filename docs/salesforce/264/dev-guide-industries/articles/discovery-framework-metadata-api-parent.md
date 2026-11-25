---
page_id: discovery-framework-metadata-api-parent
title: Discovery Framework Metadata API Types
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/discovery-framework-metadata-api-parent.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: discovery-framework
legacy_page_id: discovery_framework_metadata_api_parent.htm
fetched_at: 2026-11-25
---

# Discovery Framework Metadata API Types

Metadata API enables you to access some types and feature settings that you can customize in the user interface.

For more information about Metadata API and to find a complete reference of existing metadata types, see **[Metadata API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/)**.

The following list links to reference information for these metadata types.

- 

[AssessmentQuestion](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_assessmentquestion.htm)

Represents the container object that stores the questions required for an assessment.

- 

[AssessmentQuestionSet](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_assessmentquestionset.htm)

Represents the container object for Assessment Questions.

- 

[DocumentCategory](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_documentcategory.htm)

Represents a document category.

- 

[DocumentCategoryDocumentType](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_documentcategorydocumenttype.htm)

Represents the junction between a DocumentCategory and a DocumentType. Puts a DocumentType in a DocumentCategory.

- 

[DocumentType](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_documenttype.htm)

Represents a document type.

- 

[OmniScript](./meta-omniscript.md)

Represents an OmniScript for the Discovery Framework, which guides users through sales, service, and other business processes. For Discovery Framework, the customization type is `discoveryframework`.

- 

[Supported Metadata Channels](./discovery-framework-channels.md)

In Discovery Framework, you can create questions and question sets to categorize questions, and you can move such a dataset across multiple orgs. A metadata wrapper is automatically created for these objects.

- 

[Flow](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_visual_workflow.htm)

Represents the metadata associated with a flow that encompasses the flow’s structure, logic, and run-time behavior.

  - 

[Flow for Discovery Framework](./discovery-framework-flow-metadata-api.md)

Discovery Framework exposes additional actionType values for the FlowActionCall Metadata type.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/discovery-framework-metadata-api-parent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
