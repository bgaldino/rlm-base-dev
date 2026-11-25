---
page_id: omnistudio-metadata-api-parent
title: Omnistudio Metadata API Types
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/omnistudio-metadata-api-parent.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-overview
legacy_page_id: omnistudio_metadata_api_parent.htm
fetched_at: 2026-11-25
---

# Omnistudio Metadata API Types

Metadata API enables you to access some types and feature settings that you can customize in the user interface.

- 

**[Flow for Omnistudio](./omnistudio-flow-metadata-api.md)**

Represents the metadata associated with a flow. Use a flow to create an application that takes users through a series of pages to query and update records in the database. You can also execute logic and provide branching capability based on user input to build dynamic applications.

- 

**[DataMapperDefinition](./meta.datamapperdefinition.md)**

Represents a Data Mapper’s header configurations, such as its name and type. Data Mappers transfer and transform data between Salesforce and Omnistudio components. They act as data sources in Flexcards and as actions in Omniscripts.

- 

**[FlexcardDefinition](./meta.flexcarddefinition.md)**

Each row represents a Flexcard’s configuration such as its name and author. A Flexcard can display data and launch actions or Omniscripts. This object stores specific information about a Flexcard to render it at runtime.

- 

**[IntegrationProcdDefinition](./meta.integrationprocddefinition.md)**

Represents an Integration Procedure’s header configurations, including its type and subtype. Integration Procedures bundle server-side data operations for efficiency. They act as data sources in Flexcards and as actions in Omniscripts.

- 

**[OmniDataTransform](./meta-omnidatatransform.md)**

Represents the header configuration of a DataRaptor.

- 

**[OmniExtTrackingDef](./meta-omniexttrackingdef.md)**

Represents a connection between an OmniTrackingGroup in OmniAnalytics and a third-party Analytics system such as Google Analytics.

- 

**[OmniIntegrationProcedure](./meta-omniintegrationprocedure.md)**

Represents an Omnistudio Integration Procedure for the Discovery Framework. It enables declarative, server-side processing to perform multiple actions in a single server call, supporting sales, service, and other business workflows. For Discovery Framework, the customization type is `discoveryframework`.

- 

**[OmniInteractionAccessConfig](./meta-omniinteractionaccessconfig.md)**

Represents configuration settings for access to Omnistudio FlexCard caching and data sources.

- 

**[OmniInteractionConfig](./meta-omniinteractionconfig.md)**

Represents configuration settings for Omnistudio.

- 

**[OmniScript](./meta-omniscript.md)**

Represents an OmniScript for the Discovery Framework, which guides users through sales, service, and other business processes. For Discovery Framework, the customization type is `discoveryframework`.

- 

**[OmniscriptDefinition](./meta-omniscriptdefinition.md)**

Represents the header configuration of an Omniscript. Each row represents an Omniscript’s header configurations, such as its type, subtype, and name. An Omniscript helps build guided digital experiences. This object stores primary information about an Omniscript to render it at runtime.

- 

**[OmniStudioSettings](./meta-omnistudiosettings.md)**

Represents the settings that help administrators turn on specific Omnistudio features and capabilities at the organization level.

- 

**[OmniTrackingGroup](./meta-omnitrackinggroup.md)**

Represents a group of FlexCard and OmniScript components that have their user interactions tracked together in OmniAnalytics.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/omnistudio-metadata-api-parent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
