---
page_id: apex_class_Context_IndustriesContext.htm
title: IndustriesContext Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/apex_class_Context_IndustriesContext.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: apex_namespace_Context.htm
fetched_at: 2026-06-25
---

# IndustriesContext Class

Contains methods to create, query, persist, or delete a context. Also, query a record's
status, query a context based on tags, or update context attributes by using the available
methods.

## Namespace

[Context](#apex_class_Context_IndustriesContext "Contains methods to create, query, persist, or delete a context. Also, query a record's status, query a context based on tags, or update context attributes by using the available methods.")

- **[IndustriesContext Methods](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_methods)**  
  Learn more about the available methods with the `IndustriesContext` class.

## IndustriesContext Methods

Learn more about the available methods with the `IndustriesContext` class.

The `IndustriesContext` class includes these methods.

- **[addRecordsToContext(input)](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_addRecordsToContext)**  
  Adds one or more records at a user-defined level in the hierarchy of the context.
- **[buildContext(input)](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_buildContext)**  
  Creates a context.
- **[deleteContext(input)](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_deleteContext)**  
  Deletes a context.
- **[deleteRecords(input)](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_deleteRecords)**  
  Deletes one or more records from a context session identified by data paths.
- **[evictContextDefinition(input)](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_evictContextDefinition)**  
  Removes the details of the context definition from cache.
- **[filteringContext(input)](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_filteringContext)**  
  Builds or queries a context based on a filter criteria.
- **[getContext(input)](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_getContext)**  
  Retrieves context details.
- **[getContextTranslation(input)](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_getContextTranslation)**  
  Retrieves context mappings based on a target mapping ID.
- **[leanerQueryTags(input)](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_leanerQueryTags)**  
  Queries context tags and returns an optimized, leaner result set compared to the standard queryTags.
- **[persistContext(input)](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_persistContext)**  
  Persists the current data or state of context to the database.
- **[queryContextRecordsAndChildren(input)](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_queryContextRecordsAndChildren)**  
  Queries Context records and children based on the dataPath instead of tags.
- **[queryRecordStatus(input)](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_queryRecordStatus)**  
  Queries the status of a record.
- **[queryTags(input)](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_queryTags)**  
  Queries a context by using tags.
- **[updateContextAttributes(input)](./apex_class_Context_IndustriesContext.htm.md#apex_Context_IndustriesContext_updateContextAttributes)**  
  Updates the attributes of a context.

### addRecordsToContext(input)

Adds one or more records at a user-defined level in the hierarchy of the
context.

#### Signature

`public Map<String,Object>
addRecordsToContext(Map<String,Object> input)`

```
Context.IndustriesContext, addRecordsToContext, [Map<String,ANY>], Map<String,ANY>
```

#### Example

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();

Map<String, Object> inputAddRecord = new Map<String, Object>();
inputAddRecord.put('contextId', context.get('contextId').toString());
inputAddRecord.put('overWriteExistingRecords', true);
inputAddRecord.put('isTaggedData', false);
inputAddRecord.put('inputData', '{\"Account\":[{\"id\":\"synthetic\",\"businessObjectType\":\"Account\",\"Name\":\"test_account\"}]}');

Map<String, Object> ouputAddRecord = industriesContexts.addRecordsToContext(inputAddRecord);
```

#### Parameters

input
:   Type: Map<String,Object>
:   contextId
    :   Type: String
    :   ID of the Context to which record described in inputData is
        added.

    overWriteExistingRecords
    :   Type: Boolean
    :   Indicates if an already existing record with same ID as being
        added through inputData must be overriden.

    inputData
    :   Type: String
    :   Record data to be added to the context, hierarchical data in
        stringified format.

    isTaggedData
    :   Type: Boolean
    :   Describes if the inputData structure is using the taggedData
        Format.

#### Return Value

Type: Map<String,Object>

### buildContext(input)

Creates a context.

#### Signature

`public Map<String,Object>
buildContext(Map<String,Object> input)`

```
Context.IndustriesContext, buildContext, [Map<String,ANY>], Map<String,ANY>
```

#### Example

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();

Map<String, Object> input = new Map<String, Object>(); 

Map<String, String> metadata = new Map<String, String>(); 
metadata.put('contextDefinitionId', '11Oxx0000006PinEAE');
metadata.put('mappingId','11jxx0000004LGRAA2');

String data = '{\'Account\':[{\'id\':\'001xx000003GYK0AAO\',\'businessObjectType\':\'Account\'}]}';
input.put('data', data);
input.put('metadata', metadata);

Map<String, Object> context = industriesContexts.buildContext(input);
System.debug(context.get('contextId'));
```

#### Parameters

input
:   Type: Map<String,Object>
:   Metadata about the context and payload data required to create a context.

#### Return Value

Type: Map<String,Object>

Details containing the context ID that’s created.

### deleteContext(input)

Deletes a context.

#### Signature

`public void deleteContext(Map<String,Object> input)`

```
Context.IndustriesContext, deleteContext, [Map<String,ANY>], void
```

#### Example

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();
Map<String, Object> input = new Map<String, Object>();
input.put('contextId', '1f6ef0f4f9f361ef966d8a292db12ce90ce20bef22efb4afac431762ac71998d');
industriesContexts.deleteContext(input);
```

#### Parameters

input
:   Type: Map<String,Object>
:   Details containing the ID of the context to be deleted.

#### Return Value

Type: void

### deleteRecords(input)

Deletes one or more records from a context session identified by data
paths.

#### Signature

`public Map<String,Object>
deleteRecords(Map<String,Object> input)`

```
Context.IndustriesContext, deleteRecords, [Map<String,ANY>], Map<String,ANY>
```

#### Example

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();

Map<String, Object> input = new Map<String, Object>();
input.put('contextId', context.get('contextId').toString());

List<Map<String, Object>> dataPaths = new List<Map<String, Object>>();
Map<String, Object> dataPath1 = new Map<String, Object>();
dataPath1.put('dataPath', new List<String>{'001xx000003GbMhAAK', '003xx000004Wia5AAC'});
dataPaths.add(dataPath1);

input.put('dataPaths', dataPaths);
input.put('isPermanentDelete', false);

Map<String, Object> output = industriesContexts.deleteRecords(input);
System.debug('isSuccess: ' + output.get('isSuccess'));
```

#### Parameters

input
:   Type: Map<String,Object>
:   contextId
    :   Type: String
    :   Required. ID of the context session from which records are
        deleted.

    dataPaths
    :   Type: List<Map<String,Object>>
    :   Required. List of data path objects that identify records for
        deletion. Each object contains a `dataPath` key with record IDs that define the
        hierarchical path between the root and target record in the
        context.

    isPermanentDelete
    :   Type: Boolean
    :   Optional. Indicates whether the deletion is permanent (`true`) or not (`false`). If `false`, records are soft-deleted
        and marked as deleted within the context. If `true`, records are permanently
        removed from the context. The default value is `false`.

#### Return Value

Type: Map<String,Object>

isSuccess
:   Type: Boolean
:   Returns `true` if the delete operation
    completed successfully.

### evictContextDefinition(input)

Removes the details of the context definition from cache.

#### Signature

`public void evictContextDefinition(Map<String,ANY>
input)`

```
Context.IndustriesContext, evictContextDefinition, [Map<String,ANY>], void
```

#### Example

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();
Map<String, Object> input = new Map<String, Object>();
input.put('contextDefinitionName', 'definitionName');
industriesContexts.evictContextDefinition(input);
```

#### Parameters

input
:   Type: Map<String,ANY>
:   API name of the context definition to remove the details of the context definition
    from cache.

#### Return Value

Type: void

### filteringContext(input)

Builds or queries a context based on a filter criteria.

#### Signature

`public Map<String, Object>
industriesContexts.filteringContext(buildWithFilter);`

#### Example

Type:
BUILD

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();
Map<String, Object> buildWithFilter = new Map<String, Object>();
Map<String, Object> input = new Map<String, Object>();

Map<String, String> metadata = new Map<String, String>();
metadata.put('contextDefinitionId', '11Oxx0000006PXVEA2');
metadata.put('mappingId','11jxx0000004L59AAE');

String data = '{\'Account\':[{\'id\':\'001xx000003GYiCAAW\',\'businessObjectType\':\'Account\'}]}';
input.put('data', data);
input.put('metadata', metadata);

buildWithFilter.put('type', 'BUILD');
buildWithFilter.put('build', input);
buildWithFilter.put('filter', '{ \"buildFilter\": {\"Contact\":[{\"filterType\":\"WHERE\",\"node\":\"Contact\",\"attribute\":\"Name\",\"dataType\":\"String\",\"operands\":[\"Howard Jones\"],\"operator\":\"Equals\"}]}}');

Map<String, Object> res = industriesContexts.filteringContext(buildWithFilter);

System.debug(res);
```

Type: QUERYRECORDANDCHILDREN or
QUERYRECORDS

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();
Map<String, Object> queryWithFilter = new Map<String, Object>();
Map<String, Object> queryInput = new Map<String, Object>();

List<String> dataPath = new List<String>();
dataPath.add('001xx000003GYiCAAW');

Map<String, Object> contextDataPathInputRepresentation = new Map<String, Object>();
contextDataPathInputRepresentation.put('dataPath', dataPath);

List<Map<String, Object>> queryPaths = new List<Map<String, Object>>();
queryPaths.add(contextDataPathInputRepresentation);

queryInput.put('contextId', '44410fea80348668bebd58010279c579d611a8f686ebf71e6b2a6b1a6405160f');
queryInput.put('queryPaths', queryPaths);

queryWithFilter.put('type', 'QUERYRECORDANDCHILDREN');
queryWithFilter.put('query', queryInput);
queryWithFilter.put('filter', '{\"queryFilter\":[{\"filterType\":\"WHERE\",\"node\":\"Contact\",\"attribute\":\"Name\",\"dataType\":\"String\",\"operands\":[\"Howard Jones\"],\"operator\":\"Equals\"}]}');

Map<String, Object> res = industriesContexts.filteringContext(queryWithFilter);

System.debug(res);
```

#### Parameters

input
:   Type: Enum
:   Object defining the type of operation. Operation Metadata along with filter
    criteria to be applied on the operation. Valid values are:
    BUILD,QUERYRECORDANDCHILDREN and
    QUERYRECORDS
:   filter: String
:   Metadata about the filter object.
:   build: Map<String,Object>
:   Metadata to build the context. Only for type with value
    BUILD.
:   query: Map<String,Object>
:   Metadata to query records in the context. Only for type
    with value QUERYRECORDANDCHILDREN and
    QUERYRECORDS.

#### Return Value

Type: Map<String,Object>

Mapping of the contextId or queryResults with the requested operation type.

### getContext(input)

Retrieves context details.

#### Signature

`public Map<String,Object> getContext(Map<String,Object> input)`

```
Context.IndustriesContext, getContext, [Map<String,ANY>], Map<String,ANY>
```

#### Example

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();
Map<String, Object> input = new Map<String, Object>();

input.put('contextId', '03950312e509b6ae5c41653408fe4869efc931cc0ffd0e61f5599daa59a22309');
Map<String, Object> res = industriesContexts.getContext(input);

System.debug(res);
```

#### Parameters

input
:   Type: Map<String,Object>
:   Details containing the ID of the context to be retrieved.

#### Return Value

Type: Map<String,Object>

Details of the retrieved context.

### getContextTranslation(input)

Retrieves context mappings based on a target mapping ID.

#### Signature

`public Map<String,Object> getContextTranslation(Map<String,Object> input)`

```
Context.IndustriesContext, getContextTranslation, [Map<String,ANY>], Map<String,ANY>
```

#### Example

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();
Map<String, Object> input = new Map<String, Object>();
input.put('contextId', '1f6ef0f4f9f361ef966d8a292db12ce90ce20bef22efb4afac431762ac71998d');
input.put('contextMappingId', '11jxx0000004LGRAA2');
List<String> persistAttibuteTypes = new List<String>();
persistAttibuteTypes.add('OUTPUT');
persistAttibuteTypes.add('INPUTOUTPUT');
input.put(‘persistAttibuteTypes’,  persistAttibuteTypes);
Boolean isDependenciesEstablished = false;
input.put(‘isDependenciesEstablished’, isDependenciesEstablished);
Boolean removeRestrictedFields = false;
input.put(‘removeRestrictedFields’, removeRestrictedFields);
Map<String, Object> res = industriesContexts.getContextTranslation(input);
System.debug(res);
```

#### Parameters

input
:   Type: Map<String,Object>
:   Details of the request parameters to retrieve context mappings. The details include list of
    persisted attributes and settings to indicate whether any dependencies are established
    or restricted fields are removed.

#### Return Value

Type: Map<String,Object>

Details of the retrieved context mappings.

### leanerQueryTags(input)

Queries context tags and returns an optimized, leaner result set compared to the standard
queryTags.

#### Signature

`public Map<String,Object> leanerQueryTags(Map<String,Object> input)`

#### Usage

Use the `leanerQueryTags` method to retrieve tag values
from a context instance with optimized performance. This method returns a leaner
result set.

Before calling this method, you must first create a context instance using the `buildContext` method and obtain the `contextId`.

#### Example

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();
Map<String, Object> input = new Map<String, Object>(); 
Map<String, String> metadata = new Map<String, String>(); 
metadata.put('contextDefinitionName', 'SimpleDef');
metadata.put('mappingName','Mapping1');

String data = '{\'Account\':[{\'id\':\'001xx000003GYiBAAW\',\'businessObjectType\':\'Account\'}]}';
input.put('data', data);
input.put('metadata', metadata);                 

Map<String, Object> context = industriesContexts.buildContext(input);
System.debug(context.get('contextId'));

Map<String, Object> inputTag = new Map<String, Object>(); 
List<String> tag = new List<String>();
tag.add('Contact');
inputTag.put('contextId', (String)context.get('contextId'));
inputTag.put('tags', tag);
Map<String, Object> output = industriesContexts.leanerQueryTags(inputTag);

Map<String, Object> queryresult = (Map<String, Object>)output.get('leanerQueryTagResult');
List<String> recordIds = (List<String>)output.get('recordIds');

system.debug('Context id is: ' + output.get('contextId'));
system.debug('Record Ids list: ' + recordIds);

List<Object> contextTagDataLeanRepresentations= (List<Object>)queryresult.get('Contact_FirstName');
Map<String,Object> contextTagDataLeanRepresentation = (Map<String,Object>)contextTagDataLeanRepresentations.get(0);

for (String contextTagDataLeanRepresentationKey : contextTagDataLeanRepresentation.keySet()) {
    if(contextTagDataLeanRepresentationKey == 'tagValue'){
        if (contextTagDataLeanRepresentation.get(contextTagDataLeanRepresentationKey) instanceof Map<String, Object>) {
            Map<String, Object> accountData = (Map<String, Object>)contextTagDataLeanRepresentation.get(contextTagDataLeanRepresentationKey);

            for (String accountDataKey: accountData.keySet()) {
                Map<String, Object> attributeTagData = (Map<String, Object>)accountData.get(accountDataKey);
    
                system.debug('attributeTagData keys:: ' + attributeTagData.keySet());
                for (String attributeTagDataKey: attributeTagData.keySet()) {
                    system.debug('attributeTagDataKey:: ' + attributeTagDataKey);
                    system.debug('attributeTagDataValue:: ' + attributeTagData.get(attributeTagDataKey));
                    
                }
            }    
        } else {
            for (String key: contextTagDataLeanRepresentation.keySet()) {
                system.debug('key: ' + key);
                system.debug('value: ' +contextTagDataLeanRepresentation.get(key));
                
            }
        }
        
    }
}
```

#### Parameters

input
:   Type: Map<String,Object>
:   Input map that contains the parameters required to query the tags. Valid keys are:

    - contextId: (String) — ID of the context to query[cite:
      223].
    - tags: (List<String>) — List of tag names to query from
      the context instance. Tags serve as aliases for nodes and attributes in the context
      structure.

#### Return Value

Type: Map<String,Object>

Returns a map that contains the query results. The map includes these keys:

- `contextId` (String) — ID of the context
  instance.
- `recordIds` (List<String>) — List of record IDs
  associated with the queried tags.
- `leanerQueryTagResult` (Map<String,Object>) —
  Map that contains the query results. Each key represents a tag name, and its
  value contains the associated tag data with attribute information.

### persistContext(input)

Persists the current data or state of context to the database.

#### Signature

`public Map<String,Object> persistContext(Map<String,Object> input)`

```
Context.IndustriesContext, persistContext, [Map<String,ANY>], Map<String,ANY>
```

#### Example

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();
Map<String, Object> input = new Map<String, Object>();
input.put('contextId', '5a42181d891c60f0097d50e0e1d52d6009ee3ef593d9ea145e1f4e05996a17c6');
input.put('targetMappingId', '');
Map<String, Object> output = industriesContexts.persistContext(input);
System.debug(output.get('referenceId'));
```

#### Parameters

input
:   Type: Map<String,Object>
:   Details to persist context such as context ID and target mapping ID.

#### Return Value

Type: Map<String,Object>

Reference ID for the persisted context.

### queryContextRecordsAndChildren(input)

Queries Context records and children based on the dataPath instead of
tags.

#### Signature

`Map<String, Object>
industriesContexts.queryContextRecordsAndChildren(input: Map<String,
Object>);`

#### Example

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();
Map<String, Object> input = new Map<String, Object>();

List<String> dataPath = new List<String>();
dataPath.add('001xx000003GaX6AAK');

Map<String, Object> contextDataPathInputRepresentation = new Map<String, Object>();
contextDataPathInputRepresentation.put('dataPath', dataPath);

List<Map<String, Object>> queryPaths = new List<Map<String, Object>>();
queryPaths.add(contextDataPathInputRepresentation);

input.put('contextId', '7a823bc5f047b1b69aa059b05c3df0ccd69b1bc702e03b4f6c12740d0e277b7b');
input.put('queryPaths', queryPaths);

Map<String, Object> res = industriesContexts.queryContextRecordsAndChildren(input);

System.debug(res);
```

#### Parameters

input
:   contextId: String
:   ID of the context to be queried.
:   queryPaths: Map<String,Object>
:   List of dataPath to be queried.

#### Return Value

queryResults: Map<String,Object>

Result containing the record data.

### queryRecordStatus(input)

Queries the status of a record.

#### Signature

`public Map<String,Object> queryRecordStatus(Map<String,Object> input)`

```
Context.IndustriesContext, queryRecordStatus, [Map<String,ANY>], Map<String,ANY>
```

#### Example

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();
Map<String, Object> input = new Map<String, Object>();
input.put('contextId', '5a42181d891c60f0097d50e0e1d52d6009ee3ef593d9ea145e1f4e05996a17c6');
List<Map<String,Object>> queryPaths = new List<Map<String,Object>>();
Map<String,Object> queryPath = new Map<String,Object>();
List<String> dataPaths = new List<String>();
dataPaths.add('TestOrder123');
queryPath.put('dataPath', dataPaths);
queryPaths.add(queryPath);
input.put('queryPaths', queryPaths);
Map<String, Object> output = industriesContexts.queryRecordStatus(input);
```

#### Parameters

input
:   Type: Map<String,Object>
:   Details containing the context ID and list of record paths for context data to query the status
    for.

#### Return Value

Type: Map<String,Object>

Details containing the results of the query.

### queryTags(input)

Queries a context by using tags.

#### Signature

`public Map<String,Object> queryTags(Map<String,Object> input)`

```
Context.IndustriesContext, queryTags, [Map<String,ANY>], Map<String,ANY>
```

#### Usage

The method works on the `tagNames` of the attribute or
node.

#### Example

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();
Map<String, Object> input = new Map<String, Object>(); 
List<String> tag = new List<String>();
tag.add('contactNameTag');
input.put('contextId', '967934fc3069c04bb17df94e526052d75ab99fd87393ffad008ed07d7ac54a13');
input.put('tags', tag);
Map<String, Object> output = industriesContexts.queryTags(input);
Map<String, Object> queryresult = (Map<String, Object>)output.get('queryResult');
List<Object> contextTagDataRepresentations= (List<Object>)queryresult.get('contactNameTag');
Map<String,Object> contextTagDataRepresentation = (Map<String,Object>)contextTagDataRepresentations.get(0);
System.debug(contextTagDataRepresentation.get('dataPath'));
System.debug(contextTagDataRepresentation.get('tagValue'));
```

#### Parameters

input
:   Type: Map<String,Object>
:   Details containing the context ID and tags to be queried.

#### Return Value

Type: Map<String,Object>

Details containing the results of the query.

### updateContextAttributes(input)

Updates the attributes of a context.

#### Signature

`public Map<String,Object> updateContextAttributes(Map<String,Object> input)`

```
Context.IndustriesContext, updateContextAttributes, [Map<String,ANY>], Map<String,ANY>
```

#### Usage

Use this method to update the attributes of a context.

- This method works only with the names of the canonical structure, and not with
  tags.
- The dataType of the values must match the dataType in the canonical structure. Also, it
  must match the dataType of the field if persistence is expected later.
- The method supports attribute updates at different level. Pass an attributeMap
  corresponding to the given dataPath.
- The API works at the per-record level.

#### Example

```
Context.IndustriesContext industriesContexts = new Context.IndustriesContext();
Map<String, Object> input = new Map<String, Object>();
Map<String, Object> contextAttributeValueInputRepresentation = new Map<String, Object>();
contextAttributeValueInputRepresentation.put('attributeName', 'Name');
contextAttributeValueInputRepresentation.put('attributeValue', 'Elon');

List<Map<String, Object>> attributes = new List<Map<String, Object>>();
attributes.add(contextAttributeValueInputRepresentation);

List<String> dataPath = new List<String>();
dataPath.add('001xx000003GaX6AAK');

Map<String, Object> contextDataPathInputRepresentation = new Map<String,Object>();
contextDataPathInputRepresentation.put('dataPath', dataPath);

Map<String, Object> nodePathAndAttributesInputRepresentation = new Map<String, Object>();
nodePathAndAttributesInputRepresentation.put('nodePath', contextDataPathInputRepresentation);
nodePathAndAttributesInputRepresentation.put('attributes', attributes);

List<Map<String, Object>> nodePathAndAttributes = new List<Map<String, Object>>();
nodePathAndAttributes.add(nodePathAndAttributesInputRepresentation);

input.put('contextId', 'f4fe20aa8ffb441998a3bba42c7a0452d9b104dcadd9907810cbacff4db7c39a');
input.put('nodePathAndAttributes', nodePathAndAttributes);

Map<String, Object> res = industriesContexts.updateContextAttributes(input);

System.debug(res.get('isSuccess'));
```

#### Parameters

input
:   Type: Map<String,Object>
:   Details containing the context ID and node path. The node path contains the path of the context
    record and list of attributes to be updated with their values.

#### Return Value

Type: Map<String,Object>

Details containing the updated attribute list.
