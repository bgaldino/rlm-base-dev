---
page_id: sforce_api_objects_expssetobjectaliasfieldvw.htm
title: ExpsSetObjectAliasFieldVw
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_expssetobjectaliasfieldvw.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_standard_objects.htm
fetched_at: 2026-06-25
---

# ExpsSetObjectAliasFieldVw

Represents the virtual object that provides a consolidated view of
source object and its alias, and the source object fields and their aliases that are used
in an expression set. This object is used to check the permission level required to access
the underlying object fields associated with their field aliases. This object is
available in API version 56.0 and later.

## Supported Calls

`describeSObjects()`, `query()`

## Special Access Rules

To view this object, users need access to the source object, the usage type, and the
field level security associated with the object field aliases in the object.

## Fields

| Field | Details |
| --- | --- |
| DurableId | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The unique identifier for the field. Always retrieve this value before using it, as the value isn’t guaranteed to stay the same from one release to the next. Simplify queries by using this field instead of making multiple queries. |
| ExpsSetDefVerVarField | Type  string  Properties  Filter, Group, Nillable, Sort  Description  Identifies the variable to which this field belongs. This is a required field. |
| FieldAlias | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The alias associated with the object field that's used in the expression set. The field alias can be up to 30 characters in length. This is a required field. |
| InstalledPackageName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the package used to add the record to the org. This is a required field. |
| LastModifiedBy | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The unique identifier of the user who modified the alias last. This is a required field. |
| ManageableState | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package. This is a required field.  Possible values are:  - `beta`—Managed-Beta - `deleted`—Managed-Proposed-Deleted - `deprecated`—Managed-Proposed-Deprecated - `deprecatedEditable`—SecondGen-Installed-Deprecated - `installed`—Managed-Installed - `installedEditable`—SecondGen-Installed-Editable - `released`—Managed-Released - `unmanaged`—Unmanaged |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the namespacePrefix\_\_componentName notation. This is a required field. The namespace prefix can have one of the following values.   - In Developer Edition orgs,   NamespacePrefix is set to the   namespace prefix of the org for all objects that support it,   unless an object is in an installed managed package. In that   case, the object has the namespace prefix of the installed   managed package. This field’s value is the namespace prefix   of the Developer Edition org of the package developer. - In orgs that are not Developer Edition orgs,   NamespacePrefix is set only for   objects that are part of an installed managed package. All   other objects have no namespace prefix. |
| ObjectAlias | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The alias that corresponds to the source object whose fields are used in an expression set. In the context of an expression set, this alias is a group that contains the aliases for fields from the source object. This is a required field. |
| ObjectApiName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The API name of the source object associated with the object field aliases that are used in an expression set. |
| SourceFieldDataType | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The data type of the source object for which the object alias is defined. This is a required field.  Possible values are:  - `ActionOutput` - `Boolean` - `Currency` - `Date` - `DateTime` - `DecisionMatrix` - `DecisionTable` - `Numeric` - `Percent` - `Sobject` - `SubExpression` - `Text`  The default value is `Text`. |
| SourceFieldDecimalScale | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The number of decimal places applied to the value in the source field that's of the type Currency, Percent, or Number. |
| SourceFieldName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the source object field associated with a field alias that's used in an expression set. This is a required field. |
| UsageType | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The type of application associated with the industry that's using an expression set.  Possible values are:  - `Bre`–Default  When Business Rules Engine is enabled for a Salesforce org, the default value is '`Bre`’. Other usage types may be available to you depending on your industry solution and permission sets. |
