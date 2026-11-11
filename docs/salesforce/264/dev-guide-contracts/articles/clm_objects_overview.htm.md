---
page_id: clm_objects_overview.htm
title: Salesforce Contracts Standard Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/clm_objects_overview.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_intro.htm
fetched_at: 2026-10-13
---

# Salesforce Contracts Standard Objects

Use standard objects to work with the Salesforce Contracts application.

- 
**[ClauseCatgConfiguration](./sforce_api_objects_clausecatgconfiguration.htm.md)**  

Represents the configuration about the clause category that can be used in a response document by the user.

- 
**[ContextUseCaseMapping](./sforce_api_objects_contextusecasemapping.htm.md)**  

Represents the setup configuration details such as the context definition and mapping definitions used to invoke context service APIs. This object is available in API version 61.0 and later.

- 
**[ContractDocumentReview](./sforce_api_objects_contractdocumentreview.htm.md)**  

Represents the review process-related details, such as the reference object type and review status.  This object is available in API version 58.0 and later.

- 
**[ContractDocumentVersion](./sforce_api_objects_contractdocumentversion.htm.md)**  

Tracks contract document versions through contract lifecycle stages. This object is available in API version 56.0 and later.

- 
**[ContractDocVerContentDoc](./sforce_api_objects_contractdocvercontentdoc.htm.md)**  

Associates a contract document version with a content document. This object is available in API version 56.0 and later.

- 
**[ContractDocVersionSection](./sforce_api_objects_contractdocversionsection.htm.md)**  

Tracks contract document sections through contract lifecycle stages. This object is available in API version 56.0 and later.

- 
**[ContractExtractionResult](./sforce_api_objects_contractextractionresult.htm.md)**  

Represents contract-specific data extracted by the Contracts AI from an uploaded PDF that's ready for review. For example, account name, owner, start date, contract name, contract record type, contract term, and clauses. Before contract record creation, users can access, review, and modify the temporarily stored information. This object is available in API version 60.0 and later.

- 
**[ContractType](./sforce_api_objects_contracttype.htm.md)**  

A sub type that groups contracts with similar characteristics, such as lifecycle states, permissions, and templates and clauses used. This object is available in API version 56.0 and later.

- 
**[ContractTypeConfig](./sforce_api_objects_contracttypeconfig.htm.md)**  

The settings that define the characteristics and behavior of all contracts of that type. This object is available in API version 56.0 and later.

- 
**[DocGenerationBatchProcess](./sforce_api_objects_docgenerationbatchprocess.htm.md)**  

Represents a grouping of document generation requests associated with the batch document generation ID. Only one batch document generation request can be processed at a time. To create a new batch document generation record, pause or cancel the current record. This object is available in API version 58.0 and later.

- 
**[DocGenBtchStsChgEvent](./sforce_api_objects_docgenbtchstschgevent.htm.md)**  

Represents the change in the status of the batch document generation request. A batch document generation request groups multiple document generation requests by associating the individual requests with a batch document generation ID. This object is available in API version 62.0 and later.

- 
**[DocGenProcStsChgEvent](./sforce_api_objects_docgenprocstschgevent.htm.md)**  

Represents the change in status of a document generation request. This object is available in API version 62.0 and later.

- 
**[DocumentAuthoredContent](./sforce_api_objects_documentauthoredcontent.htm.md)**  

Represents the metadata of the content within the content boundary of a document such as a template or contract document. You can store metadata details of the marked clauses and sections in Salesforce with the document authored content.  This object is available in API version 58.0 and later.

- 
**[DocumentClause](./sforce_api_objects_documentclause.htm.md)**  

Represents a clause that can be associated with multiple documents.

- 
**[DocumentClauseContentToken](./sforce_api_objects_documentclausecontenttoken.htm.md)**  

Represents a token used in document clause content.       Supported token types include merge tokens, which are resolved at run time, and       placeholder tokens, which are provided at run time. This object is available in API       version 68.0 and later.

- 
**[DocumentClauseSet](./sforce_api_objects_documentclauseset.htm.md)**  

Represents a grouping for clauses, which can hold multiple variations of the same clause such as main clause and alternate pre-approved clauses based on language.

- 
**[DocumentEnvelope](./sforce_api_objects_documentenvelope.htm.md)**  

The container for a document that is routed for signatures. This object is available in API version 56.0 and later.

- 
**[DocumentGenerationProcess](./sforce_api_objects_documentgenerationprocess.htm.md)**  

Supports server-side document generation requests and responses. This object is available in API version 56.0 and later.

- 
**[DocumentGenerationSetting](./sforce_api_objects_documentgenerationsetting.htm.md)**  

Represents an org's settings for automatic document generation from templates. This object is available in API version 54.0 and later.

- 
**[DocumentPlaybook](./sforce_api_objects_documentplaybook.htm.md)**  

Represents a set of guidelines used to standardize how a          contract is authored, reviewed, and negotiated. This object is available in API       version 68.0 and later.

- 
**[DocumentPlaybookAssignment](./sforce_api_objects_documentplaybookassignment.htm.md)**  

Represents the assignment of a document playbook to a specific          object and record type. This object is available in API version 68.0 and       later.

- 
**[DocumentPlaybookVersion](./sforce_api_objects_documentplaybookversion.htm.md)**  

Tracks the playbook versions through content updates and          revisions. This object is available in API version 68.0 and       later.

- 
**[DocumentTemplate](./sforce_api_objects_documenttemplate.htm.md)**  

Represents information about dynamic document generation. This object is available in API version 56.0 and later.

- 
**[DocumentTemplateConfig](./sforce_api_objects_documenttemplateconfig.htm.md)**  

Represents the shadow object that supports migration of document templates between environments. The Developer field in the shadow object references the UniqueName field in the document template object and is used to retrieve the document template details. For internal use only. This object is available in API version 58.0 and later.

- 
**[DocumentTemplateSection](./sforce_api_objects_documenttemplatesection.htm.md)**  

Represents a section in a document template. A document template section can be a clause, image, context, embedded template, or signature. This object is available in API version 52.0 and later.

- 
**[ESignatureConfig](./sforce_api_objects_esignatureconfig.htm.md)**  

The settings for integrating with external eSignature providers. This object is available in API version 56.0 and later.

- 
**[ESignatureEnvelopeConfig](./sforce_api_objects_esignatureenvelopeconfig.htm.md)**  

The notification-specific settings for integrating with external eSignature providers. This object is available in API version 56.0 and later.

- 
**[ExternalDocStorageConfig](./sforce_api_objects_externaldocstorageconfig.htm.md)**  

Represents a collection of fields to configure the external document storage for an object. It includes details such as location, path, and named credentials. For example, OneDrive is defined as an External Document Storage and is associated with the Salesforce Contract object.

- 
**[GeneratedDocumentSection](./sforce_api_objects_generateddocumentsection.htm.md)**  

Represents a section of a generated document.  This object is available in API version 60.0 and later.

- 
**[ObjectStateActionDefinition](./sforce_api_objects_objectstateactiondefinition.htm.md)**  

Represents the link between the object state definition and object state transition based on a defined action.

- 
**[ObjectStateTransitionAction](./sforce_api_objects_objectstatetransitionaction.htm.md)**  

Represents a junction between object state transition and object state action definition. State transition determines the valid transition of an object from one state to another and the state action determines which action triggers which state transition.

- 
**[Obligation](./sforce_api_objects_obligation.htm.md)**  

Represents an obligation between parties to fulfill agreed conditions, such as contractual commitments. The obligation commitment assists with a strategy to achieve the desired outcome within a set timeframe and reduce risk with compliance tracking. For example, payment due dates, contract terms, renewals. This object is available in API version 59.0 and later.

- 
**[QuoteClause](./sforce_api_objects_quoteclause.htm.md)**  

Represents a clause associated with a quote. The content is       copied from a source document clause, so updates to the quote clause remain independent       of the source clause. This object is available in API version 68.0 and later.

- 
**[SalesContractLine](./sforce_api_objects_salescontractline.htm.md)**  

Stores a contract's product information, including price, quantity, and components covered. This object is available in API version 56.0 and later.

- 
**[UserEsignVendorIdentifier](./sforce_api_objects_useresignvendoridentifier.htm.md)**  

Used for integrating eSignature users. This object is available in API version 56.0 and later.

#### See Also

- [*Object Reference for the Salesforce Platform*: Overview of Salesforce Objects
       and Fields](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_concepts.htm)

- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.264.0.api.meta/api/sforce_api_quickstart_intro.htm)
