---
page_id: apex_class_industries_docgen_DocumentGenerationProcess.htm
title: DocumentGenerationProcess Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/apex_class_industries_docgen_DocumentGenerationProcess.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: apex_namespace_industries_docgen.htm
fetched_at: 2026-11-23
---

# DocumentGenerationProcess Class

The `DocumentGenerationProcess` class provides methods
to manage document generation processes.

## Namespace

[industries\_docgen](./apex_namespace_industries_docgen.htm.md "The industries_docgen namespace provides classes and methods for document generation and permission management in Salesforce Industries.")

## Example

```
Map<String, Object> parameters = new Map<String, Object>();
parameters.put('requestText','{}');
parameters.put('type','GenerateAndConvert');
parameters.put('status','InProgress');
parameters.put('title','TestTitle');
//industries_docgen.DocumentGenerationProcess.createDocumentGenerationProcess(parameters);
Type type = Type.forName('industries_docgen.DocumentGenerationProcess');
System.Callable docgen = (System.Callable) type.newInstance();
docgen.Call('createDocumentGenerationProcess',parameters);
```

This Apex code creates a
`DocumentGenerationProcess` record for server-side
document generation. This code uses a Map as input that contains all the required fields to
create an entry in the database.

- **[DocumentGenerationProcess Methods](./apex_class_industries_docgen_DocumentGenerationProcess.htm.md#apex_industries_docgen_DocumentGenerationProcess_methods)**

## DocumentGenerationProcess Methods

The following are methods for `DocumentGenerationProcess`.

- **[Call(methodName, inputMap)](./apex_class_industries_docgen_DocumentGenerationProcess.htm.md#apex_industries_docgen_DocumentGenerationProcess_Call)**  
  Invokes a method with specified input parameters for the document generation process.

### Call(methodName, inputMap)

Invokes a method with specified input parameters for the document generation
process.

#### Signature

`public Object Call(String methodName, Map<String,Object> inputMap)`

#### Parameters

- **methodName**: Type: String Name of the method to be called.
- **inputMap**: Type: `Map<String,Object>` Map that contains input parameters for the method that is called.

#### Return Value

Type: `Object`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/apex_class_industries_docgen_DocumentGenerationProcess.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
