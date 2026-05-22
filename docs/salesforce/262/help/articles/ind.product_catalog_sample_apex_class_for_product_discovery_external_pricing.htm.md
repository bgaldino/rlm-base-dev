---
article_id: ind.product_catalog_sample_apex_class_for_product_discovery_external_pricing.htm
title: "Sample: Apex Class for Product Discovery External Pricing"
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_sample_apex_class_for_product_discovery_external_pricing.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Sample: Apex Class for Product Discovery External Pricing

Use this sample Apex implementation to update product prices in a Product Discovery procedure plan. The class demonstrates how to query pricing data, fetch external values, and update the transaction response when using Apex hooks.

This example shows how to implement a custom Apex hook that interacts with external pricing logic. Use it as a starting point for building your own external pricing integrations.

SAMPLE APEX HOOK IMPLEMENTATION

    global class ApexUpdateExternalPricePostHook implements RevSignaling.SignalingApexProcessor {
    
    public virtual class BaseException extends Exception {}
    public class OtherException extends BaseException {}
    
    // Static flag to prevent recursive execution
    private static Boolean isUpdating = false;
    
    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        System.debug('=== START OF EXECUTION ===');
        String contextId = request.ctxInstanceId;
        System.debug('Context ID: ' + contextId);
        
        // Check for recursive execution
        if (isUpdating) {
            System.debug('Preventing recursive execution for context: ' + contextId);
            RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
            response.status = RevSignaling.TransactionStatus.SUCCESS;
            response.message = 'Skipping recursive execution';
            return response;
        }
        
        try {
            isUpdating = true;
            System.debug('Executing External Pricing Post Hook');
            Context.IndustriesContext industriesContext = new Context.IndustriesContext();
            
            // STEP 1 - Query PricingProduct and extract ProductId values
            Map<String, Object> inputProdQueryItem = new Map<String, Object>{
                'contextId' => contextId,
                'tags' => new List<String>{ 'PricingProduct' }
            };
                
            Map<String, Object> itemProdQueryOutput = industriesContext.queryTags(inputProdQueryItem);
            Map<String, Object> itemProdQueryResult = (Map<String, Object>) itemProdQueryOutput.get('queryResult');
            List<Object> itemProdData = (List<Object>) itemProdQueryResult.get('PricingProduct');
            System.debug('itemProdDataCount: ' + itemProdData.Size());
            System.debug('itemProdData: ' + itemProdData);
            
            Map<String, Decimal> productPricingMap = new Map<String, Decimal>();
            List<String> pricingProductList = new List<String>();
            for (Object itemObj : itemProdData) {
                Map<String, Object> itemNode = (Map<String, Object>) itemObj;
                Map<String, Object> tagMap = (Map<String, Object>) itemNode.get('tagValue');
                String pricingId = null;
                Decimal pricingProductOrigPrice = null;
                if (tagMap.containsKey('PricingId')) {
                    pricingId = (String)((Map<String, Object>) tagMap.get('PricingId')).get('tagValue');
                }
                if (tagMap.containsKey('UnitPrice')) {
                    pricingProductOrigPrice = (Decimal)((Map<String, Object>) tagMap.get('UnitPrice')).get('tagValue');
                }
                pricingProductList.add(pricingId);
                productPricingMap.put(pricingId, pricingProductOrigPrice);
            }
            
            //Step 2 - Get External Prices
            System.debug('pricingProductList: ' + pricingProductList);
            System.debug('preApexproductPricingMap: ' + productPricingMap);
            Map<String, Decimal> outputProductPricingMap = ProductPriceCalculator.calculateProductPrices(pricingProductList);
            System.debug('outputProductPricingMap: ' + outputProductPricingMap);
            
            // STEP 3 - Build update list
            List<Map<String, Object>> itemNodeUpdates = new List<Map<String, Object>>();
            
            for (Object itemObj : itemProdData) {
                Map<String, Object> itemNode1 = (Map<String, Object>) itemObj;
                List<Object> dataPath = (List<Object>) itemNode1.get('dataPath');
                System.debug('Full item dataPath: ' + JSON.serialize(dataPath));
                dataPath.remove(0);
                
                Boolean matched = false;
                String pricingId = null;
                Map<String, Object> itemNode = (Map<String, Object>) itemObj;
                Map<String, Object> tagMap = (Map<String, Object>) itemNode.get('tagValue');
                if (tagMap.containsKey('PricingId')) {
                    pricingId = (String)((Map<String, Object>) tagMap.get('PricingId')).get('tagValue');
                }
                
                Decimal newPrice = outputProductPricingMap.get(pricingId);
                System.debug('Pricing Product Id: ' + pricingId);
                System.debug('Pricing Product Price: ' + newPrice);
                
                if(newPrice == null) {
                    System.debug('No price found for product: ' + pricingId);
                    continue;
                }
                
                // Check if the price actually needs to be updated
                Decimal currentPrice = null;
                if (tagMap.containsKey('UnitPrice')) {
                    currentPrice = (Decimal)((Map<String, Object>) tagMap.get('UnitPrice')).get('tagValue');
                }
                
                if (currentPrice != newPrice) {
                    itemNodeUpdates.add(new Map<String, Object>{
                        'nodePath' => new Map<String, Object>{ 'dataPath' => dataPath },
                        'attributes' => new List<Object>{
                            new Map<String, Object>{
                                'attributeName' => 'UnitPrice',
                                'attributeValue' => newPrice
                            },
                            new Map<String, Object>{
                                'attributeName' => 'NetUnitPrice',
                                'attributeValue' => newPrice
                            },
                            new Map<String, Object>{
                                'attributeName' => 'SubTotal',
                                'attributeValue' => newPrice
                            }
                        }
                    });
                    matched = true;
                    System.debug('Added update for product: ' + pricingId + ' with new price: ' + newPrice);
                } else {
                    System.debug('No price update needed for product: ' + pricingId);
                }
                
                if (!matched) {
                    String itemCtxId = dataPath.size() > 1 ? String.valueOf(dataPath[1]) : 'UNKNOWN';
                    System.debug('No Price match found for item ' + itemCtxId);
                }
            }
            
            // STEP 4 - Submit context update only if there are changes
            if (!itemNodeUpdates.isEmpty()) {
                System.debug('Submitting ' + itemNodeUpdates.size() + ' updates to context');
                Map<String, Object> updateInput = new Map<String, Object>{
                    'contextId' => contextId,
                    'nodePathAndAttributes' => itemNodeUpdates
                };
                System.debug('Update input: ' + JSON.serializePretty(updateInput));
                Map<String, Object> result = industriesContext.updateContextAttributes(updateInput);
                System.debug('Update result: ' + JSON.serializePretty(result));
            } else {
                System.debug('No updates needed for context: ' + contextId);
            }
            
            RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
            response.status = RevSignaling.TransactionStatus.SUCCESS;
            response.message = 'External Pricing Successful';
            return response;
            
        } catch (Exception e) {
            System.debug('Error processing context ' + contextId + ': ' + e.getMessage());
            System.debug('Stack trace: ' + e.getStackTraceString());
            RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
            response.status = RevSignaling.TransactionStatus.FAILED;
            response.message = 'Error: ' + e.getMessage();
            return response;
        } finally {
            isUpdating = false;
            System.debug('=== END OF EXECUTION ===');
        }
    }
}

public class ProductPriceCalculator {
    
    public static Map<String, Decimal> calculateProductPrices(List<String> pricingIds) {
        // Fetch the product names and external IDs using the product IDs
        //List<Product2> products = [SELECT Id, Name, ExternalId FROM Product2 WHERE Id IN :productIds];
        
        //if (products.isEmpty()) {
        //    throw new IllegalArgumentException('No products found with the given IDs');
        //}

        // Initialize the map to store the product prices
        Map<String, Decimal> productPrices = new Map<String, Decimal>();

        // Calculate the price for each product
        for (String pricingId : pricingIds) {
            String productName = pricingId;
            Integer asciiSum = 0;
            for (Integer i = 0; i < productName.length(); i++) {
                asciiSum += (Integer) productName.charAt(i);
            }

            Decimal priceInGivenCurrency = asciiSum;

            // Add the product ID and price to the map
            productPrices.put(pricingId, priceInGivenCurrency);
        }

        return productPrices;
    }
}
