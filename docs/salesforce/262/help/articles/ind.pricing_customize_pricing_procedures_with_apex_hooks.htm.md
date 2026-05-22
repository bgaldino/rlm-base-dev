---
article_id: ind.pricing_customize_pricing_procedures_with_apex_hooks.htm
title: Customize Your Procedure Plans With Apex Hooks
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_customize_pricing_procedures_with_apex_hooks.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Customize Your Procedure Plans With Apex Hooks

To support unique pricing scenarios, add custom Apex logic to your pricing procedure plans. You can use Apex hooks to apply custom business logic that modifies the pricing context after a quote line is configured. Use an Apex prehook to adjust pricing based on product attributes before it's priced, and an Apex posthook to handle pricing changes for groups and other Quote object elements after pricing. When a sales rep configures a product or changes a group of quote line items, the pricing procedure plan changes the pricing based on the instructions in Apex.

REQUIRED EDITIONS
Available in: Lightning Experience
Availble in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management where Salesforce Pricing is enabled
USER
PERMISSIONS NEEDED
To create, update, and delete pricing procedures and procedure plans:	Salesforce Pricing Design Time User or Procedure Plan Access
To use pricing procedures:	Salesforce Pricing Run Time User
To define, edit, delete, set security, and set version settings for Apex classes:	Author Apex
IMPORTANT
When using the Agentforce Revenue Management process type, any Apex logic you add must be the first or last element in the Procedure Plan execution sequence.
External callouts from an Apex hook are supported only when the Place Sales Transaction request is triggered through the Salesforce user interface or Place Sales Transaction API. They aren’t supported when the request is triggered from Apex or Flow.
External callouts in Apex hooks aren’t supported when Double Persist mode is enabled. For additional guidance, contact Salesforce Customer Support.
External callouts in Apex hooks can affect performance. So, predictable Service Level Objectives (SLOs) can’t be guaranteed.
Ensure Procedure Plan Orchestration for Pricing is turned on.
From Setup, in the Quick Find box, enter Revenue Settings, then select Revenue Settings.
Find and if necessary enable the setting Procedure Plan Orchestration for Pricing.
Leave the setting Exclude Default and Sales Transaction Type Pricing Procedures disabled.
Define classes for the Apex hooks to add to your pricing procedures.
From Setup, in the Quick Find box, enter Apex, then select Apex Classes.
Select New to create a new Apex class.
In the class editor, enter the class definition.

For example, this prehook (ApexDmAttributePreHook) updates the values of dynamic attributes with the name Display_Size based on their display size. More sample classes are shown in Sample Classes for Apex Pricing Hooks at the end of these steps.

global class ApexDmlAttributePreHook implements RevSignaling.SignalingApexProcessor {

    public virtual class BaseException extends Exception {}
    public class OtherException extends BaseException {}
    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        System.debug('Executing PREHOOK');
        
        String contextId = request.ctxInstanceId;
        Context.IndustriesContext industriesContext = new Context.IndustriesContext();
        
        // STEP 1 - Query SalesTransactionItemAttribute and extract Display_Size values
        Map<String, Object> inputQueryItemAttr = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ 'SalesTransactionItemAttribute' }
        };
        Map<String, Object> itemAttrQueryOutput = industriesContext.queryTags(inputQueryItemAttr);
        Map<String, Object> itemAttrQueryResult = (Map<String, Object>) itemAttrQueryOutput.get('queryResult');
        List<Object> itemAttrData = (List<Object>) itemAttrQueryResult.get('SalesTransactionItemAttribute');

        Map<String, Decimal> parentCtxIdToDisplaySize = new Map<String, Decimal>();

        for (Object attrObj : itemAttrData) {
            Map<String, Object> attrNode = (Map<String, Object>) attrObj;
            Map<String, Object> tagMap = (Map<String, Object>) attrNode.get('tagValue');

            String attributeName = null;
            String attributeValueStr = null;
            String parentCtxId = null;

            if (tagMap.containsKey('Attribute')) {
                attributeName = (String)((Map<String, Object>) tagMap.get('Attribute')).get('tagValue');
            }
            if (tagMap.containsKey('AttributeValue')) {
                attributeValueStr = (String)((Map<String, Object>) tagMap.get('AttributeValue')).get('tagValue');
            }
            if (tagMap.containsKey('SalesTransactionItemAttrParent')) {
                parentCtxId = (String)((Map<String, Object>) tagMap.get('SalesTransactionItemAttrParent')).get('tagValue');
            }

            if (attributeName == 'Display_Size' && attributeValueStr != null && parentCtxId != null) {
                Decimal sizeValue = Decimal.valueOf(attributeValueStr.split(' ')[0]);
                parentCtxIdToDisplaySize.put(parentCtxId, sizeValue);
                System.debug('DisplaySize=' + sizeValue);
                System.debug('Matched itemCtxId=' + parentCtxId);
            }
        }

        // STEP 2 - Query SalesTransactionItem nodes
        Map<String, Object> inputQueryItem = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ 'SalesTransactionItem' }
        };
        Map<String, Object> itemQueryOutput = industriesContext.queryTags(inputQueryItem);
        Map<String, Object> itemQueryResult = (Map<String, Object>) itemQueryOutput.get('queryResult');
        List<Object> itemData = (List<Object>) itemQueryResult.get('SalesTransactionItem');

        // STEP 3 - Build update list
        List<Map<String, Object>> itemNodeUpdates = new List<Map<String, Object>>();

        for (Object itemObj : itemData) {
            Map<String, Object> itemNode = (Map<String, Object>) itemObj;
            List<Object> dataPath = (List<Object>) itemNode.get('dataPath');
            System.debug('Full item dataPath: ' + JSON.serialize(dataPath));

            Boolean matched = false;
            for (String ctxKey : parentCtxIdToDisplaySize.keySet()) {
                if (dataPath.contains(ctxKey)) {
                    Decimal newPrice = parentCtxIdToDisplaySize.get(ctxKey);
                    System.debug('DisplaySize match found for item ' + ctxKey);
                    dataPath.remove(0); // Remove contextId

                    itemNodeUpdates.add(new Map<String, Object>{
                        'nodePath' => new Map<String, Object>{ 'dataPath' => dataPath },
                        'attributes' => new List<Object>{
                            new Map<String, Object>{
                                'attributeName' => 'UnitPrice',
                                'attributeValue' => newPrice
                            }
                        }
                    });
                    matched = true;
                    break;
                }
            }

            if (!matched) {
                String itemCtxId = dataPath.size() > 1 ? String.valueOf(dataPath[1]) : 'UNKNOWN';
                System.debug('No DisplaySize match found for item ' + itemCtxId);
            }
        }

        // STEP 4 - Submit context update
        if (!itemNodeUpdates.isEmpty()) {
            Map<String, Object> updateInput = new Map<String, Object>{
                'contextId' => contextId,
                'nodePathAndAttributes' => itemNodeUpdates
            };

            System.debug('--- PREHOOK: SUBMITTING CONTEXT UPDATE ---');
            System.debug(JSON.serializePretty(updateInput));
            industriesContext.updateContextAttributes(updateInput);
        }

        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        response.status = RevSignaling.TransactionStatus.SUCCESS;
        //response.status = RevSignaling.TransactionStatus.FAILED;
        //response.message = 'An error occurred during the processing...';
        return response;
    }
    
}
Save the class definition.
From Setup, in the Quick Find box, enter Procedure Plan, then select Procedure Plan Definitions.
In the Definition Names column, select a procedure plan definition to edit.
From the procedure plan definition, in Procedure Plan Sections, select Add to add a new section.
Select Standard.
Name the section, for example PreApex for an Apex prehook.
In Section Type, select Apex then Save.
Expand the new section.
For Phases, select Pricing and for Resolution Type select Default.
In the Apex selection box that appears, enter the Apex class you defined above, for example ApexDmlAttributePreHook, then select Save.
Add additional prehooks and posthooks as needed.
Select Manage Sections to rearrange prehooks above the Pricing Procedure section and posthooks below it.
Save your changes to the Procedure Plan definition.
EXAMPLE Sample Classes for Apex Pricing Hooks

Prehook: Update the discount percentage to 2% on all lines in the context (for example, quote lines).


global class ApexDmlDiscountUpdatePreHook implements RevSignaling.SignalingApexProcessor {

    public virtual class BaseException extends Exception {}
    public class OtherException extends BaseException {}
    
    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        System.debug('Executing PREHOOK');
        
        String contextId = request.ctxInstanceId;
        Context.IndustriesContext industriesContext = new Context.IndustriesContext();
        
        Integer randomDiscountPercentage = 2;

        // STEP 2 - Query SalesTransactionItem nodes
        Map<String, Object> inputQueryItem = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ 'SalesTransactionItem' }
        };
        Map<String, Object> itemQueryOutput = industriesContext.queryTags(inputQueryItem);
        Map<String, Object> itemQueryResult = (Map<String, Object>) itemQueryOutput.get('queryResult');
        List<Object> itemData = (List<Object>) itemQueryResult.get('SalesTransactionItem');

        System.debug('QLI itemData=' + itemData);

        // STEP 3 - Build update list
        List<Map<String, Object>> itemNodeUpdates = new List<Map<String, Object>>();

        for (Object itemObj : itemData) {
            Map<String, Object> itemNode = (Map<String, Object>) itemObj;
            List<Object> dataPath = (List<Object>) itemNode.get('dataPath');
            System.debug('Full item dataPath: ' + JSON.serialize(dataPath));

            Boolean matched = false;
            dataPath.remove(0); // Remove contextId

            itemNodeUpdates.add(new Map<String, Object>{
                'nodePath' => new Map<String, Object>{ 'dataPath' => dataPath },
                'attributes' => new List<Object>{
                    new Map<String, Object>{
                        'attributeName' => 'Discount',
                        'attributeValue' => randomDiscountPercentage
                    }
                }
            });
            matched = true;

            if (!matched) {
                String itemCtxId = dataPath.size() > 1 ? String.valueOf(dataPath[1]) : 'UNKNOWN';
                System.debug('No DisplaySize match found for item ' + itemCtxId);
            }
        }

        // STEP 4 - Submit context update
        if (!itemNodeUpdates.isEmpty()) {
            Map<String, Object> updateInput = new Map<String, Object>{
                'contextId' => contextId,
                'nodePathAndAttributes' => itemNodeUpdates
            };

            System.debug('--- PREHOOK: SUBMITTING CONTEXT UPDATE ---');
            System.debug(JSON.serializePretty(updateInput));
            industriesContext.updateContextAttributes(updateInput);
        }

        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        response.status = RevSignaling.TransactionStatus.SUCCESS;
        //response.status = RevSignaling.TransactionStatus.FAILED;
        //response.message = 'An error occurred during the processing...';
        return response;
    }
}

Prehook: Call an external resource to fetch a quantity value.


global class ApexDmlQuantityCalloutPreHook implements RevSignaling.SignalingApexProcessor {

    public virtual class BaseException extends Exception {}
    public class OtherException extends BaseException {}
    
    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        System.debug('Executing PREHOOK');
        
        String contextId = request.ctxInstanceId;
        Context.IndustriesContext industriesContext = new Context.IndustriesContext();
        
        // STEP 1 - External Callout Test
        Integer randomNumber = getRandomNumber();
        System.debug(' Random Number from API: ' + randomNumber);

        // STEP 2 - Query SalesTransactionItem nodes
        Map<String, Object> inputQueryItem = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ 'SalesTransactionItem' }
        };
        Map<String, Object> itemQueryOutput = industriesContext.queryTags(inputQueryItem);
        Map<String, Object> itemQueryResult = (Map<String, Object>) itemQueryOutput.get('queryResult');
        List<Object> itemData = (List<Object>) itemQueryResult.get('SalesTransactionItem');

        System.debug('QLI itemData=' + itemData);

        // STEP 3 - Build update list
        List<Map<String, Object>> itemNodeUpdates = new List<Map<String, Object>>();

        for (Object itemObj : itemData) {
            Map<String, Object> itemNode = (Map<String, Object>) itemObj;
            List<Object> dataPath = (List<Object>) itemNode.get('dataPath');
            System.debug('Full item dataPath: ' + JSON.serialize(dataPath));

            Boolean matched = false;
            dataPath.remove(0); // Remove contextId
    
            itemNodeUpdates.add(new Map<String, Object>{
                'nodePath' => new Map<String, Object>{ 'dataPath' => dataPath },
                'attributes' => new List<Object>{
                    new Map<String, Object>{
                        'attributeName' => 'Quantity',
                        'attributeValue' => randomNumber
                    }
                }
            });
            matched = true;

            if (!matched) {
                String itemCtxId = dataPath.size() > 1 ? String.valueOf(dataPath[1]) : 'UNKNOWN';
                System.debug('No DisplaySize match found for item ' + itemCtxId);
            }
        }

        // STEP 4 - Submit context update
        if (!itemNodeUpdates.isEmpty()) {
            Map<String, Object> updateInput = new Map<String, Object>{
                'contextId' => contextId,
                'nodePathAndAttributes' => itemNodeUpdates
            };

            System.debug('--- PREHOOK: SUBMITTING CONTEXT UPDATE ---');
            System.debug(JSON.serializePretty(updateInput));
            industriesContext.updateContextAttributes(updateInput);
        }

        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        response.status = RevSignaling.TransactionStatus.SUCCESS;
        //response.status = RevSignaling.TransactionStatus.FAILED;
        //response.message = 'An error occurred during the processing...';
        return response;
    }
    
    // External callout
    private Integer getRandomNumber() {
        String endpoint = 'https://www.random.org/integers/?num=1&min=1&max=100&col=1&base=10&format=plain&rnd=new';
        Http http = new Http();
        HttpRequest req = new HttpRequest();
        req.setEndpoint(endpoint);
        req.setMethod('GET');
        req.setTimeout(5000);

        try {
            HttpResponse res = http.send(req);
            if (res.getStatusCode() == 200) {
                System.debug('Fetched prices from external service');
                return Integer.valueOf(res.getBody().trim());
            } else {
                System.debug(' Callout failed: ' + res.getStatus());
            }
        } catch (Exception ex) {
            System.debug(' Exception during callout: ' + ex.getMessage());
        }
        return 10;
    }
}

Prehook: Trigger an update to the price a product if its Attribute Name is Display and its Attribute Value is 1080p Built-in Display, or if its Attribute Name is Printer and its Attribute Value is Laser.


global class ApexDmlMultiAttributePreHook implements RevSignaling.SignalingApexProcessor {

    public virtual class BaseException extends Exception {}
    public class OtherException extends BaseException {}
    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        System.debug('Executing PREHOOK');
        
        String contextId = request.ctxInstanceId;
        Context.IndustriesContext industriesContext = new Context.IndustriesContext();
        
        // STEP 1 - Query SalesTransactionItemAttribute and extract Display_Size values
        Map<String, Object> inputQueryItemAttr = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ 'SalesTransactionItemAttribute' }
        };
        Map<String, Object> itemAttrQueryOutput = industriesContext.queryTags(inputQueryItemAttr);
        Map<String, Object> itemAttrQueryResult = (Map<String, Object>) itemAttrQueryOutput.get('queryResult');
        List<Object> itemAttrData = (List<Object>) itemAttrQueryResult.get('SalesTransactionItemAttribute');

        Map<String, Decimal> parentCtxIdToAttribute = new Map<String, Decimal>();

        for (Object attrObj : itemAttrData) {
            Map<String, Object> attrNode = (Map<String, Object>) attrObj;
            Map<String, Object> tagMap = (Map<String, Object>) attrNode.get('tagValue');

            String attributeName = null;
            String attributeValueStr = null;
            String parentCtxId = null;

            System.debug('TagMap ' + tagMap);
            if (tagMap.containsKey('Attribute')) {
                attributeName = (String)((Map<String, Object>) tagMap.get('Attribute')).get('tagValue');
            }
            if (tagMap.containsKey('AttributeValue')) {
                attributeValueStr = (String)((Map<String, Object>) tagMap.get('AttributeValue')).get('tagValue');
            }
            if (tagMap.containsKey('SalesTransactionItemAttrParent')) {
                parentCtxId = (String)((Map<String, Object>) tagMap.get('SalesTransactionItemAttrParent')).get('tagValue');
            }
            
            if (attributeName == 'Display' && attributeValueStr == '1080p Built-in Display' && parentCtxId != null) {
               Decimal defaultDisplayCost = 1000.00;
               parentCtxIdToAttribute.put(parentCtxId, defaultDisplayCost);
               System.debug('Display=' + defaultDisplayCost);
               System.debug('Matched itemCtxId=' + parentCtxId);
            }
            
            if (attributeName == 'Printer' && attributeValueStr == 'Laser' && parentCtxId != null) {
               Decimal defaultLaserPrinterCost = 500.00;
               parentCtxIdToAttribute.put(parentCtxId, defaultLaserPrinterCost);
               System.debug('Printer=' + defaultLaserPrinterCost);
               System.debug('Matched itemCtxId=' + parentCtxId);
            }
        }

        // STEP 2 - Query SalesTransactionItem nodes
        Map<String, Object> inputQueryItem = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ 'SalesTransactionItem' }
        };
        Map<String, Object> itemQueryOutput = industriesContext.queryTags(inputQueryItem);
        Map<String, Object> itemQueryResult = (Map<String, Object>) itemQueryOutput.get('queryResult');
        List<Object> itemData = (List<Object>) itemQueryResult.get('SalesTransactionItem');

        // STEP 3 - Build update list
        List<Map<String, Object>> itemNodeUpdates = new List<Map<String, Object>>();

        for (Object itemObj : itemData) {
            Map<String, Object> itemNode = (Map<String, Object>) itemObj;
            List<Object> dataPath = (List<Object>) itemNode.get('dataPath');
            System.debug('Full item dataPath: ' + JSON.serialize(dataPath));

            Boolean matched = false;
            for (String ctxKey : parentCtxIdToAttribute.keySet()) {
                if (dataPath.contains(ctxKey)) {
                    Decimal newPrice = parentCtxIdToAttribute.get(ctxKey);
                    System.debug('Attribute match found for item ' + ctxKey);
                    System.debug('Attribue with new price ' + newPrice);
                    dataPath.remove(0); // Remove contextId

                    itemNodeUpdates.add(new Map<String, Object>{
                        'nodePath' => new Map<String, Object>{ 'dataPath' => dataPath },
                        'attributes' => new List<Object>{
                            new Map<String, Object>{
                                'attributeName' => 'UnitPrice',
                                'attributeValue' => newPrice
                            }
                        }
                    });
                    matched = true;
                    break;
                }
            }

            if (!matched) {
                String itemCtxId = dataPath.size() > 1 ? String.valueOf(dataPath[1]) : 'UNKNOWN';
                System.debug('No DisplaySize match found for item ' + itemCtxId);
            }
        }

        // STEP 4 - Submit context update
        if (!itemNodeUpdates.isEmpty()) {
            Map<String, Object> updateInput = new Map<String, Object>{
                'contextId' => contextId,
                'nodePathAndAttributes' => itemNodeUpdates
            };

            System.debug('--- PREHOOK: SUBMITTING CONTEXT UPDATE ---');
            System.debug(JSON.serializePretty(updateInput));
            industriesContext.updateContextAttributes(updateInput);
        }

        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        response.status = RevSignaling.TransactionStatus.SUCCESS;
        //response.status = RevSignaling.TransactionStatus.FAILED;
        //response.message = 'An error occurred during the processing...';
        return response;
    }
    
}



Prehook: Apply a random discount percentage for all lines in the context.


global class ApexDmlRandomDiscountPreHook implements RevSignaling.SignalingApexProcessor {

    public virtual class BaseException extends Exception {}
    public class OtherException extends BaseException {}
    
    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        System.debug('Executing PREHOOK');
        
        String contextId = request.ctxInstanceId;
        Context.IndustriesContext industriesContext = new Context.IndustriesContext();
        
        Integer randomDiscountPercentage = getRandomNumber();

        // STEP 2 - Query SalesTransactionItem nodes
        Map<String, Object> inputQueryItem = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ 'SalesTransactionItem' }
        };
        Map<String, Object> itemQueryOutput = industriesContext.queryTags(inputQueryItem);
        Map<String, Object> itemQueryResult = (Map<String, Object>) itemQueryOutput.get('queryResult');
        List<Object> itemData = (List<Object>) itemQueryResult.get('SalesTransactionItem');

        System.debug('QLI itemData=' + itemData);

        // STEP 3 - Build update list
        List<Map<String, Object>> itemNodeUpdates = new List<Map<String, Object>>();

        for (Object itemObj : itemData) {
            Map<String, Object> itemNode = (Map<String, Object>) itemObj;
            List<Object> dataPath = (List<Object>) itemNode.get('dataPath');
            System.debug('Full item dataPath: ' + JSON.serialize(dataPath));

            Boolean matched = false;
            dataPath.remove(0); // Remove contextId

            itemNodeUpdates.add(new Map<String, Object>{
                'nodePath' => new Map<String, Object>{ 'dataPath' => dataPath },
                'attributes' => new List<Object>{
                    new Map<String, Object>{
                        'attributeName' => 'Discount',
                        'attributeValue' => randomDiscountPercentage
                    }
                }
            });
            matched = true;

            if (!matched) {
                String itemCtxId = dataPath.size() > 1 ? String.valueOf(dataPath[1]) : 'UNKNOWN';
                System.debug('No DisplaySize match found for item ' + itemCtxId);
            }
        }

        // STEP 4 - Submit context update
        if (!itemNodeUpdates.isEmpty()) {
            Map<String, Object> updateInput = new Map<String, Object>{
                'contextId' => contextId,
                'nodePathAndAttributes' => itemNodeUpdates
            };

            System.debug('--- PREHOOK: SUBMITTING CONTEXT UPDATE ---');
            System.debug(JSON.serializePretty(updateInput));
            industriesContext.updateContextAttributes(updateInput);
        }

        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        response.status = RevSignaling.TransactionStatus.SUCCESS;
        //response.status = RevSignaling.TransactionStatus.FAILED;
        //response.message = 'An error occurred during the processing...';
        return response;
    }
        // External callout
    public static Integer getRandomNumber() {
        String endpoint = 'https://www.random.org/integers/?num=1&min=1&max=100&col=1&base=10&format=plain&rnd=new';
        Http http = new Http();
        HttpRequest req = new HttpRequest();
        req.setEndpoint(endpoint);
        req.setMethod('GET');
        req.setTimeout(5000);

        try {
            HttpResponse res = http.send(req);
            if (res.getStatusCode() == 200) {
                System.debug('Fetched prices from external service');
                return Integer.valueOf(res.getBody().trim());
            } else {
                System.debug(' Callout failed: ' + res.getStatus());
            }
        } catch (Exception ex) {
            System.debug(' Exception during callout: ' + ex.getMessage());
        }
        return 10;
    }

}

Prehook: Update a dynamic attribute value with random value from a callout to an external resource.


global class ApexDmlAttributeExternalCalloutPreHook implements RevSignaling.SignalingApexProcessor {

    public virtual class BaseException extends Exception {}
    public class OtherException extends BaseException {}
    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        System.debug('Executing PREHOOK');
        
        String contextId = request.ctxInstanceId;
        Context.IndustriesContext industriesContext = new Context.IndustriesContext();
        
        // STEP 1 - Query SalesTransactionItemAttribute and extract Display_Size values
        Map<String, Object> inputQueryItemAttr = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ 'SalesTransactionItemAttribute' }
        };
        Map<String, Object> itemAttrQueryOutput = industriesContext.queryTags(inputQueryItemAttr);
        Map<String, Object> itemAttrQueryResult = (Map<String, Object>) itemAttrQueryOutput.get('queryResult');
        List<Object> itemAttrData = (List<Object>) itemAttrQueryResult.get('SalesTransactionItemAttribute');

        Map<String, Decimal> parentCtxIdToDisplaySize = new Map<String, Decimal>();

        for (Object attrObj : itemAttrData) {
            Map<String, Object> attrNode = (Map<String, Object>) attrObj;
            Map<String, Object> tagMap = (Map<String, Object>) attrNode.get('tagValue');

            String attributeName = null;
            String attributeValueStr = null;
            String parentCtxId = null;

            if (tagMap.containsKey('Attribute')) {
                attributeName = (String)((Map<String, Object>) tagMap.get('Attribute')).get('tagValue');
            }
            if (tagMap.containsKey('AttributeValue')) {
                attributeValueStr = (String)((Map<String, Object>) tagMap.get('AttributeValue')).get('tagValue');
            }
            if (tagMap.containsKey('SalesTransactionItemAttrParent')) {
                parentCtxId = (String)((Map<String, Object>) tagMap.get('SalesTransactionItemAttrParent')).get('tagValue');
            }

            if (attributeName == 'Display_Size' && attributeValueStr != null && parentCtxId != null) {
                Decimal sizeValue = getRandomNumber();
                parentCtxIdToDisplaySize.put(parentCtxId, sizeValue);
                System.debug('DisplaySize=' + sizeValue);
                System.debug('Matched itemCtxId=' + parentCtxId);
            }
        }

        // STEP 2 - Query SalesTransactionItem nodes
        Map<String, Object> inputQueryItem = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ 'SalesTransactionItem' }
        };
        Map<String, Object> itemQueryOutput = industriesContext.queryTags(inputQueryItem);
        Map<String, Object> itemQueryResult = (Map<String, Object>) itemQueryOutput.get('queryResult');
        List<Object> itemData = (List<Object>) itemQueryResult.get('SalesTransactionItem');

        // STEP 3 - Build update list
        List<Map<String, Object>> itemNodeUpdates = new List<Map<String, Object>>();

        for (Object itemObj : itemData) {
            Map<String, Object> itemNode = (Map<String, Object>) itemObj;
            List<Object> dataPath = (List<Object>) itemNode.get('dataPath');
            System.debug('Full item dataPath: ' + JSON.serialize(dataPath));

            Boolean matched = false;
            for (String ctxKey : parentCtxIdToDisplaySize.keySet()) {
                if (dataPath.contains(ctxKey)) {
                    Decimal newPrice = parentCtxIdToDisplaySize.get(ctxKey);
                    System.debug('DisplaySize match found for item ' + ctxKey);
                    dataPath.remove(0); // Remove contextId

                    itemNodeUpdates.add(new Map<String, Object>{
                        'nodePath' => new Map<String, Object>{ 'dataPath' => dataPath },
                        'attributes' => new List<Object>{
                            new Map<String, Object>{
                                'attributeName' => 'UnitPrice',
                                'attributeValue' => newPrice
                            }
                        }
                    });
                    matched = true;
                    break;
                }
            }

            if (!matched) {
                String itemCtxId = dataPath.size() > 1 ? String.valueOf(dataPath[1]) : 'UNKNOWN';
                System.debug('No DisplaySize match found for item ' + itemCtxId);
            }
        }

        // STEP 4 - Submit context update
        if (!itemNodeUpdates.isEmpty()) {
            Map<String, Object> updateInput = new Map<String, Object>{
                'contextId' => contextId,
                'nodePathAndAttributes' => itemNodeUpdates
            };

            System.debug('--- PREHOOK: SUBMITTING CONTEXT UPDATE ---');
            System.debug(JSON.serializePretty(updateInput));
            industriesContext.updateContextAttributes(updateInput);
        }

        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        response.status = RevSignaling.TransactionStatus.SUCCESS;
        //response.status = RevSignaling.TransactionStatus.FAILED;
        //response.message = 'An error occurred during the processing...';
        return response;
    }
    
        // External callout
    private Integer getRandomNumber() {
        String endpoint = 'https://www.random.org/integers/?num=1&min=1&max=100&col=1&base=10&format=plain&rnd=new';
        Http http = new Http();
        HttpRequest req = new HttpRequest();
        req.setEndpoint(endpoint);
        req.setMethod('GET');
        req.setTimeout(5000);

        try {
            HttpResponse res = http.send(req);
            if (res.getStatusCode() == 200) {
                System.debug('Fetched prices from external service');
                return Integer.valueOf(res.getBody().trim());
            } else {
                System.debug(' Callout failed: ' + res.getStatus());
            }
        } catch (Exception ex) {
            System.debug(' Exception during callout: ' + ex.getMessage());
        }
        return 10;
    }
}

Posthook: Update the description of each line in the context.


global class ApexDmlDescriptionPostHook implements RevSignaling.SignalingApexProcessor {

    public virtual class BaseException extends Exception {}
    public class OtherException extends BaseException {}
    
    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        System.debug('Executing POSTHOOK');
        
        String contextId = request.ctxInstanceId;
        Context.IndustriesContext industriesContext = new Context.IndustriesContext();
        
        String randomDescription = 'via Post Apex Pricing Hook';

        // STEP 2 - Query SalesTransactionItem nodes
        Map<String, Object> inputQueryItem = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ 'SalesTransactionItem' }
        };
        Map<String, Object> itemQueryOutput = industriesContext.queryTags(inputQueryItem);
        Map<String, Object> itemQueryResult = (Map<String, Object>) itemQueryOutput.get('queryResult');
        List<Object> itemData = (List<Object>) itemQueryResult.get('SalesTransactionItem');

        System.debug('QLI itemData=' + itemData);

        // STEP 3 - Build update list
        List<Map<String, Object>> itemNodeUpdates = new List<Map<String, Object>>();

        for (Object itemObj : itemData) {
            Map<String, Object> itemNode = (Map<String, Object>) itemObj;
            List<Object> dataPath = (List<Object>) itemNode.get('dataPath');
            System.debug('Full item dataPath: ' + JSON.serialize(dataPath));

            Boolean matched = false;
            dataPath.remove(0); // Remove contextId

            itemNodeUpdates.add(new Map<String, Object>{
                'nodePath' => new Map<String, Object>{ 'dataPath' => dataPath },
                'attributes' => new List<Object>{
                    new Map<String, Object>{
                        'attributeName' => 'SalesTrxnItemDescription',
                        'attributeValue' => randomDescription
                    }
                }
            });
            matched = true;

            if (!matched) {
                String itemCtxId = dataPath.size() > 1 ? String.valueOf(dataPath[1]) : 'UNKNOWN';
                System.debug('No DisplaySize match found for item ' + itemCtxId);
            }
        }

        // STEP 4 - Submit context update
        if (!itemNodeUpdates.isEmpty()) {
            Map<String, Object> updateInput = new Map<String, Object>{
                'contextId' => contextId,
                'nodePathAndAttributes' => itemNodeUpdates
            };

            System.debug('--- PREHOOK: SUBMITTING CONTEXT UPDATE ---');
            System.debug(JSON.serializePretty(updateInput));
            industriesContext.updateContextAttributes(updateInput);
        }

        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        response.status = RevSignaling.TransactionStatus.SUCCESS;
        //response.status = RevSignaling.TransactionStatus.FAILED;
        //response.message = 'An error occurred during the processing...';
        return response;
    }
}

Preehook: Invoke Apex pricing hook from a test class

@isTest
private class ApexDmlAttributePreHookTest {
    @isTest
    static void testExecute() {
        // Build or mock the context manually
        Context.IndustriesContext industriesContext = new Context.IndustriesContext();

        Map<String, Object> input = new Map<String, Object>();
        Map<String, String> metadata = new Map<String, String>();
        metadata.put('contextDefinitionId', '<Your_Actual_ContextDefinitionId>');
        metadata.put('mappingId', '<Your_Actual_MappingId>');

        // Create sample data (for example, a quote or related records)
       // Replace id with your Quote ID
      // If you are testing an order, replace the businessObjectType with Order
        String data = '{\'Quote\':[{' +
                      '\'id\':\'0Q0xx000003GYK0AAO\',' +
                      '\'businessObjectType\':\'Quote\'}]}';
        input.put('data', data);
        input.put('metadata', metadata);

        Map<String, Object> context = industriesContext.buildContext(input);
        String contextId = (String) context.get('contextId');

        RevSignaling.ProcedurePlan dummyPlan = new RevSignaling.ProcedurePlan();
        RevSignaling.TransactionRequest request = new RevSignaling.TransactionRequest(dummyPlan, contextId);

        Test.startTest();
        // Instantiate and execute your Apex hook class
        ApexDmlAttributePreHook processor = new ApexDmlAttributePreHook();
        RevSignaling.TransactionResponse response = processor.execute(request);

        Test.stopTest();

        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status);
    }
}

global class ApexDmlAttributePreHook implements RevSignaling.SignalingApexProcessor {

    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        String contextId = request.ctxInstanceId;
        Context.IndustriesContext industriesContext = new Context.IndustriesContext();

        Map<String, Object> inputQuery = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ 'SalesTransactionItem' }
        };

        Map<String, Object> result = industriesContext.queryTags(inputQuery);
        System.debug('result==' + result);

        // Add your prehook logic here
        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        response.status = RevSignaling.TransactionStatus.SUCCESS;
        response.message = 'Prehook executed';
        return response;
    }
}


Preehook: Refactor Apex hook using an interface


// STEP 1 - Define a wrapper interface
public interface IndustriesContextInterface {
    Map<String, Object> queryTags(Map<String, Object> input);
    void updateContextAttributes(Map<String, Object> input);
}

//STEP 2 - Wrap the real IndustriesContext class
public class RealIndustriesContext implements IndustriesContextInterface {
    Context.IndustriesContext realCtx = new Context.IndustriesContext();

    public Map<String, Object> queryTags(Map<String, Object> input) {
        return realCtx.queryTags(input);
    }

    public void updateContextAttributes(Map<String, Object> input) {
        realCtx.updateContextAttributes(input);
    }
}

//STEP 3 - Inject the interface into the refactored Apex hook
global class ApexDmlAttributePreHook_Refactored implements RevSignaling.SignalingApexProcessor {
    public virtual class BaseException extends Exception {}
    public class OtherException extends BaseException {}

    private IndustriesContextInterface industriesContext;

    public ApexDmlAttributePreHook_Refactored() {
        this(new RealIndustriesContext());
    }

    public ApexDmlAttributePreHook_Refactored(IndustriesContextInterface ctx) {
        this.industriesContext = ctx;
    }

    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        System.debug('Executing PREHOOK');
        String contextId = request.ctxInstanceId;

        // Query attributes
        Map<String, Object> itemAttrQueryOutput = industriesContext.queryTags(new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ 'SalesTransactionItemAttribute' }
        });

        Map<String, Object> itemAttrQueryResult = (Map<String, Object>) itemAttrQueryOutput.get('queryResult');
        List<Object> itemAttrData = (List<Object>) itemAttrQueryResult.get('SalesTransactionItemAttribute');

        Map<String, Decimal> parentCtxIdToDisplaySize = new Map<String, Decimal>();

        for (Object attrObj : itemAttrData) {
            Map<String, Object> tagMap = (Map<String, Object>) ((Map<String, Object>) attrObj).get('tagValue');
            if (tagMap.get('Attribute') != null && tagMap.get('AttributeValue') != null && tagMap.get('SalesTransactionItemAttrParent') != null) {
                String name = (String)((Map<String, Object>) tagMap.get('Attribute')).get('tagValue');
                if (name == 'Display_Size') {
                    String valStr = (String)((Map<String, Object>) tagMap.get('AttributeValue')).get('tagValue');
                    String parentCtxId = (String)((Map<String, Object>) tagMap.get('SalesTransactionItemAttrParent')).get('tagValue');
                    Decimal displaySize = Decimal.valueOf(valStr.split(' ')[0]);
                    parentCtxIdToDisplaySize.put(parentCtxId, displaySize);
                }
            }
        }

        // Query line items
        Map<String, Object> itemQueryOutput = industriesContext.queryTags(new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ 'SalesTransactionItem' }
        });

        Map<String, Object> itemQueryResult = (Map<String, Object>) itemQueryOutput.get('queryResult');
        List<Object> itemData = (List<Object>) itemQueryResult.get('SalesTransactionItem');

        List<Map<String, Object>> updates = new List<Map<String, Object>>();
        for (Object itemObj : itemData) {
            Map<String, Object> node = (Map<String, Object>) itemObj;
            List<Object> path = (List<Object>) node.get('dataPath');

            for (String ctxId : parentCtxIdToDisplaySize.keySet()) {
                if (path.contains(ctxId)) {
                    path.remove(0);
                    updates.add(new Map<String, Object>{
                        'nodePath' => new Map<String, Object>{ 'dataPath' => path },
                        'attributes' => new List<Object>{
                            new Map<String, Object>{
                                'attributeName' => 'UnitPrice',
                                'attributeValue' => parentCtxIdToDisplaySize.get(ctxId)
                            }
                        }
                    });
                    break;
                }
            }
        }

        if (!updates.isEmpty()) {
            industriesContext.updateContextAttributes(new Map<String, Object>{
                'contextId' => contextId,
                'nodePathAndAttributes' => updates
            });
        }

        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        response.status = RevSignaling.TransactionStatus.SUCCESS;
        response.message = 'Prehook executed';
        return response;
    }
}

//STEP 4 - Create a mock implementation for testing
@IsTest
public class MockIndustriesContext implements IndustriesContextInterface {

    public Map<String, Object> queryTags(Map<String, Object> input) {
        String tag = ((List<String>)input.get('tags'))[0];
        Map<String, Object> result = new Map<String, Object>();

        if (tag == 'SalesTransactionItemAttribute') {
            List<Object> attributes = new List<Object>();
            attributes.add(new Map<String, Object>{
                'tagValue' => new Map<String, Object>{
                    'Attribute' => new Map<String, Object>{ 'tagValue' => 'Display_Size' },
                    'AttributeValue' => new Map<String, Object>{ 'tagValue' => '14.5 Inches' },
                    'SalesTransactionItemAttrParent' => new Map<String, Object>{ 'tagValue' => 'itemCtx123' }
                }
            });
            result.put('SalesTransactionItemAttribute', attributes);
        }
        else if (tag == 'SalesTransactionItem') {
            List<Object> items = new List<Object>();
            items.add(new Map<String, Object>{
                'dataPath' => new List<Object>{ 'ctxId123', 'itemCtx123' }
            });
            result.put('SalesTransactionItem', items);
        }

        return new Map<String, Object>{ 'queryResult' => result };
    }

    public void updateContextAttributes(Map<String, Object> input) {
        System.debug('Mock updateContextAttributes called with: ' + JSON.serializePretty(input));
        // Optionally add asserts to verify this input during test execution
    }
}

//STEP 5 - Write the test class
@IsTest
private class ApexDmlAttributePreHookTest_Refactored {

    @IsTest
    static void testExecute_withValidDisplaySize() {
        IndustriesContextInterface mockCtx = new MockIndustriesContext();
        ApexDmlAttributePreHook_Refactored hook = new ApexDmlAttributePreHook_Refactored(mockCtx);

        // Build a test context
        Context.IndustriesContext industriesContexts = new Context.IndustriesContext();
        Map<String, Object> input = new Map<String, Object>();
        Map<String, String> metadata = new Map<String, String>();
        metadata.put('contextDefinitionId', '<Replace with ContextDefinitionId>');
        metadata.put('mappingId','Replace with MappingId');

        String data = '{\'Quote\':[{\'id\':\'0Q0xx000003GYK0AAO\',\'businessObjectType\':\'Quote\'}]}';
        input.put('data', data);
        input.put('metadata', metadata);

        Map<String, Object> context = industriesContexts.buildContext(input);
        System.debug(context.get('contextId'));

        RevSignaling.ProcedurePlan dummyPlan = new RevSignaling.ProcedurePlan();
        RevSignaling.TransactionRequest request = new RevSignaling.TransactionRequest(dummyPlan, context);

        RevSignaling.TransactionResponse response = hook.execute(request);

        System.debug('response==' + response);
        System.assertEquals(RevSignaling.TransactionStatus.SUCCESS, response.status);
    }
}
Configure Apex Hooks in a Product Discovery Procedure Plan
Use Apex sections in a Product Discovery procedure plan to run custom pricing logic, such as fetching prices from an external system. The order of Apex and Pricing sections determines how prices are applied. You can include multiple Pricing and Apex sections, but only one Qualification section.
Sample: Apex Class for Product Discovery External Pricing
Use this sample Apex implementation to update product prices in a Product Discovery procedure plan. The class demonstrates how to query pricing data, fetch external values, and update the transaction response when using Apex hooks.
Example: Use Apex Hooks to Extend Pricing Logic
See how Apex hooks interact with Pricing sections when configured as pre- or post-hooks in a Product Discovery procedure plan.
Best Practices for Apex Pricing Hooks
Follow these best practices when implementing Apex hooks in your pricing procedure plans to optimize performance and avoid unexpected results.
