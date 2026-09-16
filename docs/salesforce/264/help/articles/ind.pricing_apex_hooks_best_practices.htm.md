---
article_id: ind.pricing_apex_hooks_best_practices.htm
title: Best Practices for Apex Pricing Hooks
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_apex_hooks_best_practices.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_customize_pricing_procedures_with_apex_hooks.htm
fetched_at: 2026-09-07
---

# Best Practices for Apex Pricing Hooks

Follow these best practices when implementing Apex hooks in your pricing procedure plans to optimize performance and avoid unexpected results.

Apex Governor Limits

Apex hooks in procedure plans run within the same Apex transaction, so the central processing unit timer is cumulative across all operations. Be mindful of governor limits when writing hook logic, especially for transactions with many line items.

For current limit values, see Execution Governors and Limits in the Apex Developer Guide.

Query Only the Tags You Need

Avoid querying broad entity-level tags like SalesTransactionItem, which return every attribute for every item. Instead, request only the specific tags your hook logic requires.

Not recommended: Querying broad tags


// BAD: Returns ALL attributes for every SalesTransactionItem
Map<String, Object> input = new Map<String, Object>{
    'contextId' => contextId,
    'tags' => new List<String>{ 'SalesTransactionItem' }
};
Map<String, Object> output = industriesContext.queryTags(input);
   

Recommended: Query only specific tags


// GOOD: Query only the specific tags (attributes) you need
Map<String, Object> input = new Map<String, Object>{
    'contextId' => contextId,
    'tags' => new List<String>{ 'LineItem', 'LineItemQuantity', 'ItemProductCode' }
};
Map<String, Object> output = industriesContext.queryTags(input);
   

Recommended: Combine specific tags with leanerQueryTags


// BETTER: Combine specific tags with leanerQueryTags for maximum efficiency
Map<String, Object> input = new Map<String, Object>{
    'contextId' => contextId,
    'tags' => new List<String>{ 'LineItem', 'LineItem$DmlStatus',
        'LineItemQuantity', 'ItemProductCode' }
};
Map<String, Object> output = industriesContext.leanerQueryTags(input);
   
Use leanerQueryTags Instead of queryTags

The Context.IndustriesContext class provides two methods for querying context data. Use leanerQueryTags wherever possible for better performance.

queryTags (heavy) — Returns full context nodes with nested tag-value maps and dataPath arrays. Every attribute is wrapped in a map with 6 fields (tagValue, dmlStatus, isDirty, isNodeLevelTag, tagPath, contextDataPathBuilder) per attribute per item. All attributes for the tag are returned regardless of what you need.

leanerQueryTags (lightweight) — Returns a compact structure with flat tag values and index-based record ID references. Tag values have only 3 fields (tagValue, recordIdIndexesForPath, isNodeLevelTag). Record IDs are deduplicated into a shared recordsInfo list; nodes reference them by index.

The following example shows how to call leanerQueryTags and process its output.


String contextId = request.ctxInstanceId;
Context.IndustriesContext industriesContext = new Context.IndustriesContext();

Map<String, Object> input = new Map<String, Object>{
    'contextId' => contextId,
    'tags' => new List<String>{ 'LineItem', 'ItemProductCode', 'LineItemQuantity' }
};
Map<String, Object> output = industriesContext.leanerQueryTags(input);

// Access the leaner result structure
Map<String, Object> queryResult = (Map<String, Object>)
    output.get('leanerQueryTagResult');
List<Object> recordsInfo = (List<Object>) output.get('recordsInfo');
List<Object> lineItems = (List<Object>) queryResult.get('LineItem');

// Iterate over tag values — each tag is flat
List<Object> productCodes = (List<Object>) queryResult.get('ItemProductCode');
for (Object obj : productCodes) {
    Map<String, Object> tagNode = (Map<String, Object>) obj;
    String productCode = (String) tagNode.get('tagValue');
    List<Integer> indexes = (List<Integer>) tagNode.get('recordIdIndexesForPath');
    // recordsInfo entries are maps with 'recordId' and 'dmlStatusOrdinal'
    String itemId = (String) ((Map<String, Object>)
        recordsInfo.get(indexes[1])).get('recordId');
}
   

The leanerQueryTags output structure looks like this:


{
  "isSuccess": true,
  "contextId": "...",
  "leanerQueryTagResult": {
    "LineItem": [
      { "recordIdIndexesForPath": [0, 1], "tagValue": "0QLVW000001LxvN4AS", "isNodeLevelTag": false },
      { "recordIdIndexesForPath": [0, 2], "tagValue": "0QLVW000001Lxus4AC", "isNodeLevelTag": false }
    ],
    "ItemProductCode": [
      { "recordIdIndexesForPath": [0, 1], "tagValue": "PROD-001", "isNodeLevelTag": false },
      { "recordIdIndexesForPath": [0, 2], "tagValue": "PROD-002", "isNodeLevelTag": false }
    ]
  },
  "recordsInfo": [
    { "recordId": "0Q0VW0000011qC50AI", "dmlStatusOrdinal": null },
    { "recordId": "0QLVW000001LxvN4AS", "dmlStatusOrdinal": null },
    { "recordId": "0QLVW000001Lxus4AC", "dmlStatusOrdinal": null }
  ]
}
   
NOTE Update your existing Apex pricing hooks to use leanerQueryTags instead of queryTags where possible.
Migrate from queryTags to leanerQueryTags

When migrating existing hooks from queryTags to leanerQueryTags, apply these key transforms.

Input: Use individual tags instead of broad tags


// Before (queryTags — broad tag):
Map<String, Object> input = new Map<String, Object>{
    'contextId' => contextId,
    'tags' => new List<String>{ 'SalesTransactionItem' }
};
Map<String, Object> output = industriesContext.queryTags(input);
   

// After (leanerQueryTags — specific tags):
Map<String, Object> input = new Map<String, Object>{
    'contextId' => contextId,
    'tags' => new List<String>{ 'LineItem', 'LineItem$DmlStatus',
        'ItemProductCode', 'LineItemQuantity' }
};
Map<String, Object> output = industriesContext.leanerQueryTags(input);
   

Output: Different top-level key


// Before:
Map<String, Object> queryResult = (Map<String, Object>) output.get('queryResult');
List<Object> items = (List<Object>) queryResult.get('SalesTransactionItem');
   

// After:
Map<String, Object> queryResult = (Map<String, Object>)
    output.get('leanerQueryTagResult');
List<Object> recordsInfo = (List<Object>) output.get('recordsInfo');
List<Object> lineItems = (List<Object>) queryResult.get('LineItem');
   

Node access: Flat values instead of nested maps


// Before (queryTags — nested map extraction):
for (Object itemObj : items) {
    Map<String, Object> itemNode = (Map<String, Object>) itemObj;
    Map<String, Object> tagValueMap = (Map<String, Object>) itemNode.get('tagValue');
    String productCode = (String) ((Map<String, Object>)
        tagValueMap.get('ItemProductCode')).get('tagValue');
    Decimal quantity = (Decimal) ((Map<String, Object>)
        tagValueMap.get('LineItemQuantity')).get('tagValue');
}
   

// After (leanerQueryTags — flat value, iterated per tag):
List<Object> productCodes = (List<Object>) queryResult.get('ItemProductCode');
List<Object> recordsInfo = (List<Object>) output.get('recordsInfo');

for (Object obj : productCodes) {
    Map<String, Object> tagNode = (Map<String, Object>) obj;
    String productCode = (String) tagNode.get('tagValue');
    List<Integer> indexes = (List<Integer>) tagNode.get('recordIdIndexesForPath');
    String itemId = (String) ((Map<String, Object>)
        recordsInfo.get(indexes[1])).get('recordId');
}
   

Record IDs: Index references instead of dataPath


// Before (queryTags):
List<Object> dataPath = (List<Object>) itemNode.get('dataPath');
// dataPath = ['contextId', 'txnId', 'itemId'] — 3 elements, first is contextId
dataPath.remove(0);
String transactionId = (String) dataPath.get(0);
   

// After (leanerQueryTags):
List<Object> recordsInfo = (List<Object>) output.get('recordsInfo');
List<Integer> indexes = (List<Integer>) tagNode.get('recordIdIndexesForPath');
String transactionId = (String) ((Map<String, Object>)
    recordsInfo.get(indexes[0])).get('recordId');
String itemId = (String) ((Map<String, Object>)
    recordsInfo.get(indexes[1])).get('recordId');
   
Use the tagIdIndexMap Pattern

When processing multiple tags in a single loop, use a tagIdIndexMap to map each tag name to its position in the recordIdIndexesForPath array. This lets you correctly extract IDs at each hierarchy level:


Map<String, Integer> tagIdIndexMap = new Map<String, Integer>{
    'LineItem' => 1,            // item-level tag, ID at index 1
    'LineItem$DmlStatus' => 1,  // item-level tag, ID at index 1
    'LineItemQuantity' => 1,    // item-level tag, ID at index 1
    'BusinessUnit__c' => 0,     // transaction-level tag, ID at index 0
    'Contract' => 0             // transaction-level tag, ID at index 0
};
   
Index 0 = transaction-level (the path has one element: [txnId])
Index 1 = item-level (the path has two elements: [txnId, itemId])
Index 2 = detail-level (the path has three elements: [txnId, itemId, detailId])
Filter Deleted Items

Skip deleted items at the start of your iteration loop to avoid unnecessary processing. Request LineItem$DmlStatus as a separate tag in your query:


private static final String DML_DELETED = 'DELETED';

for (Map<String, Object> item : salesTransactionInstance.salesTransactionItems) {
    String dmlStatus = (String) item.get('LineItem$DmlStatus');

    if (dmlStatus == DML_DELETED) {
        continue; // Skip deleted items
    }

    // Process active items...
}
   
Read $DmlStatus as a Separate Tag

When querying specific tags (the recommended approach), DML status is not embedded in the tag metadata. You must request LineItem$DmlStatus as a separate tag. This applies to both queryTags and leanerQueryTags.


// Add LineItem$DmlStatus to your tags list
'tags' => new List<String>{ 'LineItem', 'LineItem$DmlStatus', 'ItemProductCode' }

// Access it like any other tag in the result
Map<String, Object> dmlNode = (Map<String, Object>) dmlStatusValues.get(i);
String dmlStatus = String.valueOf(dmlNode.get('tagValue'));
