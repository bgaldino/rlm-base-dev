/*
Context Service — full runtime lifecycle in one Apex transaction.

Works on ANY org (no pilot needed): buildContext → leanerQueryTags →
updateContextAttributes → persistContext, all in one request where the
contextId never expires.

BEFORE RUNNING: fill in the 3 placeholders below. Get them from:
  python scripts/context_service/definition/describe_context.py \
    --target-org <your-sf-alias> --developer-name RLM_SalesTransactionContext

Surface differences (Apex vs REST vs Flow):
  - Apex updateContextAttributes: key "nodePathAndAttributes" (native
    List<Map<String,Object>>). The stringified "nodePathAndUpdatedValues" key
    ALWAYS throws UnexpectedException — do NOT use it from direct Apex.
  - REST PATCH /contexts/attributes: same key "nodePathAndAttributes", parsed
    JSON body — functionally identical to the Apex native shape.
  - Flow invocable updateContextAttributes: uses the stringified
    "nodePathAndUpdatedValues" key with TAG names (tagValues/tagName shape).
    The invocable adapter deserializes it internally.

dataPath semantics (verified on 262 / v67.0, both pilot and non-pilot):
  - dataPath = [recordId]        → value ACTUALLY MUTATES
  - dataPath = [nodeName]        → isSuccess=true but SILENT NO-OP
  - dataPath = []                → isSuccess=true but SILENT NO-OP
  Record IDs are REQUIRED for mutations to take effect.

Usage:
  sf apex run --file scripts/apex/contextServiceLifecycle.apex \
    --target-org rlm-base__beta
*/

// ─── CONFIGURATION (fill these in) ──────────────────────────────────────────
String contextDefinitionId = '11OEc000005QeRxMAK';  // from describe_context.py
String mappingId           = '11jEc0000Bi8TIoIQM';  // QuoteEntitiesMapping (default)
String recordId            = '';                      // a real Quote Id (0Q0...) — leave empty for synthetic
// ─────────────────────────────────────────────────────────────────────────────

Context.IndustriesContext ctx = new Context.IndustriesContext();

// 1. BUILD — hydrate (id-only pulls live data server-side, 0 SOQL)
//    businessObjectType MUST be the MAPPED SObject name ("Quote"), NOT the node name.
Map<String,String> md = new Map<String,String>{
    'contextDefinitionId' => contextDefinitionId,
    'mappingId'           => mappingId
};

String dataPayload;
if (String.isNotBlank(recordId)) {
    dataPayload = '{"SalesTransaction":[{"id":"' + recordId + '","businessObjectType":"Quote"}]}';
} else {
    dataPayload = '{"SalesTransaction":[{"id":"","businessObjectType":"Quote","SalesTransactionName":"Apex Lifecycle Test","Status":"Draft","CurrencyIsoCode":"USD"}]}';
}

Map<String,Object> buildInput = new Map<String,Object>{
    'metadata' => md,
    'data'     => dataPayload
};

Map<String,Object> buildResult = ctx.buildContext(buildInput);
String contextId = (String) buildResult.get('contextId');
System.debug('=== BUILD: contextId = ' + contextId);
System.debug('=== BUILD: isSuccess = ' + buildResult.get('isSuccess'));

// 2. QUERY TAGS — read values by tag name (not attribute/field name)
//    Tag names come from describe_context.py (attributeTags[].name on each attribute).
List<String> tagsToQuery = new List<String>{
    'SalesTransactionName', 'Status', 'CurrencyIsoCode'
};

Map<String,Object> queryInput = new Map<String,Object>{
    'contextId' => contextId,
    'tags'      => tagsToQuery
};

Map<String,Object> queryResult = ctx.leanerQueryTags(queryInput);
System.debug('=== QUERY TAGS: isSuccess = ' + queryResult.get('isSuccess'));
System.debug('=== QUERY TAGS: recordIds = ' + queryResult.get('recordIds'));
System.debug('=== QUERY TAGS: leanerQueryTagResult = ' + queryResult.get('leanerQueryTagResult'));

// 3. UPDATE ATTRIBUTES — stage an in-memory edit (native List<Map> shape)
//    Key: "nodePathAndAttributes" (List<Map<String,Object>>).
//    Uses ATTRIBUTE names (not tag names).
//    dataPath MUST contain RECORD IDs — node names / empty = silent no-op.
//    ⚠ Do NOT use the stringified "nodePathAndUpdatedValues" key — it ALWAYS
//    throws UnexpectedException from direct Apex (it's only for the Flow adapter).
if (String.isNotBlank(recordId)) {
    List<String> dataPath = new List<String>();
    dataPath.add(recordId);

    Map<String,Object> nodePath = new Map<String,Object>();
    nodePath.put('dataPath', dataPath);

    Map<String,Object> attrValue = new Map<String,Object>();
    attrValue.put('attributeName', 'SalesTransactionName');
    attrValue.put('attributeValue', 'Updated via Apex');

    List<Map<String,Object>> attributes = new List<Map<String,Object>>();
    attributes.add(attrValue);

    Map<String,Object> nodePathAndAttr = new Map<String,Object>();
    nodePathAndAttr.put('nodePath', nodePath);
    nodePathAndAttr.put('attributes', attributes);

    List<Map<String,Object>> nodePathAndAttributes = new List<Map<String,Object>>();
    nodePathAndAttributes.add(nodePathAndAttr);

    Map<String,Object> updateInput = new Map<String,Object>();
    updateInput.put('contextId', contextId);
    updateInput.put('nodePathAndAttributes', nodePathAndAttributes);

    Map<String,Object> updateResult = ctx.updateContextAttributes(updateInput);
    System.debug('=== UPDATE: ' + updateResult);

    // VERIFY the update took (query uses TAG names, not attribute names)
    Map<String,Object> verifyResult = ctx.leanerQueryTags(new Map<String,Object>{
        'contextId' => contextId,
        'tags'      => new List<String>{'SalesTransactionName'}
    });
    System.debug('=== VERIFY: SalesTransactionName = ' + verifyResult.get('leanerQueryTagResult'));
} else {
    System.debug('=== UPDATE: skipped (requires a real recordId in dataPath to actually mutate — empty/node-name dataPath silently no-ops)');
}

// 5. PERSIST — write dirty values back to the mapped SObjects (async)
//    Returns a referenceId (16P); confirm via AsyncOperationTracker.
//    ⚠ Default QuoteEntitiesMapping carries non-updateable fields — a dirty
//    persist through it will fail (errorNodes). Use a custom mapping with only
//    updateable fields for production writeback.
Map<String,Object> persistInput = new Map<String,Object>{
    'contextId'       => contextId,
    'targetMappingId' => mappingId
};
Object persistResult = ctx.persistContext(persistInput);
System.debug('=== PERSIST: referenceId = ' + persistResult);
System.debug('=== Check: SELECT Status, Response FROM AsyncOperationTracker WHERE JobType=\'ContextPersistence\' ORDER BY CreatedDate DESC LIMIT 1');

// 6. DELETE — evict the instance
ctx.deleteContext(new Map<String,Object>{'contextId' => contextId});
System.debug('=== DELETE: evicted contextId ' + contextId);
System.debug('=== DONE — full lifecycle complete');
