---
page_id: sforce_api_objects_expressionsetview.htm
title: ExpressionSetView
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_expressionsetview.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_standard_objects.htm
fetched_at: 2026-06-25
---

# ExpressionSetView

Represents a virtual object that provides a consolidated view of
file-based expression set. File-based expression sets are read-only templates. To be able
to modify file-based expression sets, you must clone them first.  This object is
available in API version 55.0 and later.

## Supported Calls

`describeSObjects()`,
`query()`

## Fields

| Field | Details |
| --- | --- |
| Description | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The description of an expression set. |
| DurableId | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The ID of the expression set. |
| ExpressionSetDetails | Type  textarea  Properties  Nillable  Description  The details of the expression set in JSON format, which includes information such as name, version, created date, and elements contained in the expression set. |
| HasContextDefinitionRef | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the executable expression set template references an executable context definition (`true`) or not (`false`). The default value is False. Available in API version 60.0 and later.  The default value is `false`. |
| IsExecutable | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the expression set template is executable (`true`) or not (`false`). Available in API version 60.0 and later.  The default value is `false`. |
| IsTemplate | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the expression set is a template (`true`) or not (`false`). When installed from managed packages, expression sets can’t be viewed or cloned by subscribers because of intellectual property (IP) protection. But when those expression sets are templates, subscribers can open them in a builder, clone them, and customize the clones.  The default value is `false`. |
| LastModifiedBy | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the user that last updated the expression set view. |
| Name | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the file-based or database expression set. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `namespacePrefix__componentName` notation.  The namespace prefix can have one of the following values.   - In Developer Edition orgs,   NamespacePrefix is set to the   namespace prefix of the org for all objects that support it,   unless an object is in an installed managed package. In that   case, the object has the namespace prefix of the installed   managed package. This field’s value is the namespace prefix   of the Developer Edition org of the package developer. - In orgs that aren’t Developer Edition orgs,   NamespacePrefix is set only for   objects that are part of an installed managed package. All   other objects have no namespace prefix. |
| UsageType | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The type of industry or the application within the industry that's using the template. Available in API version 60.0 and later. Possible value is:  - Bre—Business Rules Engine  When Business Rules Engine is enabled for a Salesforce instance, the default value is `Bre`. Other usage types may be available to you depending on your industry solution and permission sets. |
| UsageTypeLabel | Type  string  Properties  Filter, Group, Nillable, Sort  Description  Specifies the label of the usage type that's associated with an expression set template |

## Usage

Use expression set templates as reference to build your own expression sets. Expression
set templates are read-only files that contain rules that can run end-to-end. Save a
template as an expression set to use it as-is, or modify the expression set for your
business requirement.
