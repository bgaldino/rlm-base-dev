---
page_id: apex_class_industries_docgen_DocumentTemplate.htm
title: DocumentTemplate Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/apex_class_industries_docgen_DocumentTemplate.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: apex_namespace_industries_docgen.htm
fetched_at: 2026-10-13
---

# DocumentTemplate Class

The `DocumentTemplate` class provides methods to manage
        document generation
        templates.

## Namespace

[industries_docgen](./apex_namespace_industries_docgen.htm.md)

## Example

```
System.Callable connect = (System.Callable) type.newInstance();
Map<String, Object> inputMap = new Map<String, Object>();
inputMap.put('documentTemplateId', templateId);
docTemplate = SObjectProxy.of(DocGenObjectMappings.getSObjectType(DocGenObjectMappings.DOCUMENT_TEMPLATE_STR).newSObject());
Map<String, Object> mapData = (Map<String, Object>)connect.Call('getNamespaceByDocumentTemplateId', inputMap);
```

This
                GET request retrieves the Namespace field from the DocumentTemplate entity, using
                the documentTemplate ID as input.

- 
**[DocumentTemplate Methods](./apex_class_industries_docgen_DocumentTemplate.htm.md#apex_industries_docgen_DocumentTemplate_methods)**  

## DocumentTemplate Methods

The following are methods for `DocumentTemplate`.

- 
**[Call(methodName, inputMap)](./apex_class_industries_docgen_DocumentTemplate.htm.md#apex_industries_docgen_DocumentTemplate_Call)**  

Invokes a method with input parameters to manage document templates.

### Call(methodName, inputMap)

Invokes a method with input parameters to manage document templates.

#### Signature

`public Object Call(String methodName, Map<String,ANY> inputMap)`

#### Parameters

- 
**methodName**: Type: String Name of the method to be called.

- 
**inputMap**: Type: `Map<String,ANY>` Map that contains input parameters for the method that is called.

#### Return Value

Type: `Object`
