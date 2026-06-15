---
article_id: ind.qocal_advanced_detail_line_pricing_for_custom_and_derived_products.htm
title: Use Advanced Transaction Detail Line Pricing to Map Custom Fields
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_advanced_detail_line_pricing_for_custom_and_derived_products.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Use Advanced Transaction Detail Line Pricing to Map Custom Fields

Users can update custom fields on sales transaction items or sales transaction item details through pricing procedures by using the Advanced Detail Line Pricing feature. With this feature, users no longer need to use custom triggers or flows to update those fields. This feature is useful for amendment, renewal, and cancellation use cases.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To set up and use advanced detail line pricing:	

Salesforce admin

AND

Pricing Design Time User permission set

Before you begin, complete these tasks.

To turn on the Advanced Detail Line Pricing feature, in Setup, find and select Revenue Settings, and then turn on the Advanced Detail Line Pricing setting.
Configure your pricing procedure.
Add Context Tag Mappings to the Pricing Procedure Map Line Item Element Using JSON
To configure a pricing procedure to use advanced detail line pricing, copy and paste the map line item JSON to a pricing procedure in Revenue Pricing.
Add Context Tag Mappings to the Discovery Procedure Map Line Item Element Using JSON
To configure a discovery procedure to use advanced detail line pricing with derived-pricing products, copy and paste the map line item for derived pricing JSON to a discovery procedure in Revenue Pricing.
Update Revenue Pricing Procedure

To configure advanced detail line pricing, modify your revenue pricing procedure.

From the App Launcher, find and select Pricing Procedures, and then select a pricing procedure to update.
Modify the pricing procedure by adding a new map line item element as the second element next to the pricing setting in the pricing procedure.
Add context tag mappings to the map line item.

Input Variable

	

Output Variable




LineItem

	

SalesTrxnItemDetailSource




LineItemQuantity

	

ItemDetailQuantity




NetUnitPrice

	

ItemDetailNetUnitPrice




price_water_fall

	

DetailPriceWaterfallIdentifier




InputUnitPrice

	

ItemDetailUnitPrice




ItemBillingReference

	

ItemDetailBillingReference




ItemNetTotalPrice

	

ItemDetailTotalPrice




TotalLineAmount

	

ItemDetailTotalLineAmount




EffectiveFrom

	

ItemDetailEffectiveFrom__std




EffectiveTo

	

ItemDetailEffectiveTo__std




PricingTermCount

	

ItemDetailPricingTermCount__std




itemTransientEndDate

	

ItemDetailTransientEndDate__std




ItemPricingSource

	

ItemDetailPricingSource__std




DerivedPricingAttribute

	

ItemDetailDerivedPricingAttribute__std




ItemGroupSummarySubtotal

	

ItemDetailGroupSummaryTotal__std




ListPrice

	

ItemDetailListPrice__std




IsContracted

	

ItemDetailIsContracted__std




ItemContractPrice

	

ItemDetailContractPrice__std




STI_TenantName__c

	

STID_TenantName__c

After adding the context tag mappings, you’ll see the default mappings between SalesTransaction and SalesTransactionItemDetail with updated context definitions.
Update Derived Pricing Discovery Procedure

If you're using derived pricing, make additional changes to your discovery procedure after completing changes to your revenue pricing procedure. These changes are necessary to determine valid contributing and derived products.

From the App Launcher, find and select Discovery Procedures, and then select a discovery procedure to update.
Add two new elements to the discovery procedure to price derived products: Discovery Settings and Map Line Item.
Add these variables to discovery settings.
Input Variable: Line Item
Output Variable: LineItem
Add these variables to the map line item.
Input Variable: SalesTransactionItem
Output Variable: SalesTransactionItemDetail

Add these additional variables to the map line item.

Input Variable

	

Output Variable




LineItem

	

SalesTrxnItemDetailSource




EffectiveFrom

	

ItemDetailEffectiveFrom__std




EffectiveTo

	

ItemDetailEffectiveTo__std




DerivedPricingAttribute

	

ItemDetailDerivedPricingAttribute__std

Support custom fields by using pricing procedures for amend, renew, and cancel (ARC) use cases.
Custom field setup is applicable if you use ARC APIs and want to use custom fields.
Add custom fields to the QuoteLineItem, QuoteLineItem Detail, OrderProduct, and OrderProductDetails objects.
In the context definition, create an entry for these custom fields in both SalesTransactionItem and SalesTransactionItemDetail nodes.
Create the required mappings in QuoteEntitiesMapping and OrderEntitiesMapping.
Modify the revenue pricing procedure for custom fields.
In the pricing procedure, modify the MapLineItem element to add a mapping between SalesTransactionItem.CustomField and SalesTransactionItemDetail.CustomField.
Create any necessary customization elements within the pricing procedure to assign a value to SalesTransactionItem.CustomField.

The pricing procedure automatically detects if a specific line has detail entries and writes to SalesTransactionItemDetail.CustomField if they exist. Otherwise, it writes to SalesTransactionItem.CustomField.

During new sale transactions, CustomField on SalesTransactionItem is populated. For ARC scenarios with detail lines, the detail line is written to CustomField on SalesTransactionItemDetail. If no detail lines are created for ARC, the detail line is it written to CustomField on SalesTransactionItem.

To write custom fields on QuoteLineItem or OrderProducts with detail lines, complete this additional setup involving procedure plans and Apex classes.
Enable a procedure plan. In Setup, find and select Revenue Settings, and turn on the Procedure Plan Orchestration for Pricing setting.
Create a procedure plan for the quote and order.
In the procedure plan, verify all steps include the MapLineItem element. Modify the mappings based on the fields used in the pricing procedure.
Use this ApexCustomFieldHandler Apex class example, which you can enhance to update multiple custom fields if required. This class queries SalesTransactionItem and SalesTransactionItemDetail nodes, extracts custom field values from detail items, and then updates the corresponding custom fields on SalesTransactionItem.
EXAMPLE
global class ApexCustomFieldHandler implements RevSignaling.SignalingApexProcessor {

    public virtual class BaseException extends Exception {}
    public class OtherException extends BaseException {}
    
    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        
        String contextId = request.ctxInstanceId;
        Context.IndustriesContext industriesContext = new Context.IndustriesContext();
        

        // STEP 2 - Query SalesTransactionItem nodes
        Map<String, Object> inputQueryItem = new Map<String, Object>{
            'contextId' => contextId,
            'tags' => new List<String>{ 'SalesTransactionItem', 'SalesTransactionItemDetail' }
        };
        Map<String, Object> itemQueryOutput = industriesContext.queryTags(inputQueryItem);
        Map<String, Object> itemQueryResult = (Map<String, Object>) itemQueryOutput.get('queryResult');
        List<Object> itemData = (List<Object>) itemQueryResult.get('SalesTransactionItem');
        List<Object> itemDetailData = (List<Object>) itemQueryResult.get('SalesTransactionItemDetail');


        Map<String, String> salesTransactionItemIdToCustomAggregatedValue = new Map<String, String>();
        
        // STEP 3 - Custom Field Value from SalesTransactionItemDetail
        for(Object itemDetailObj : itemDetailData) {
            Map<String, Object> itemDetailNode = (Map<String, Object>) itemDetailObj;
            Map<String, Object> detailTagMap = (Map<String, Object>) itemDetailNode.get('tagValue');
            
            String lineItemId = (String)((Map<String, Object>) detailTagMap.get('SalesTrxnItemDetailParent')).get('tagValue');
            String cfValue = (String)((Map<String, Object>) detailTagMap.get('STID_TenantName__c')).get('tagValue');
            
            System.debug('Custom Field Value for Detail Item' + cfValue);
            if(cfValue != null) {
                salesTransactionItemIdToCustomAggregatedValue.put(lineItemId, cfValue);
            }
        }


        // STEP 4 - Build update list
        List<Map<String, Object>> itemNodeUpdates = new List<Map<String, Object>>();

        for (Object itemObj : itemData) {
            Map<String, Object> itemNode = (Map<String, Object>) itemObj;
            Map<String, Object> tagMap = (Map<String, Object>) itemNode.get('tagValue');
            
            String lineItemId = (String)((Map<String, Object>) tagMap.get('LineItem')).get('tagValue');
            
            List<Object> dataPath = (List<Object>) itemNode.get('dataPath');

            dataPath.remove(0); // Remove contextId

            itemNodeUpdates.add(new Map<String, Object>{
                'nodePath' => new Map<String, Object>{ 'dataPath' => dataPath },
                'attributes' => new List<Object>{
                    new Map<String, Object>{
                        'attributeName' => 'STI_TenantName__c',
                        'attributeValue' => salesTransactionItemIdToCustomAggregatedValue.get(lineItemId)
                    }
                }
            });
        }

        // STEP 5 - Create collection context update
        if (!itemNodeUpdates.isEmpty()) {
            Map<String, Object> updateInput = new Map<String, Object>{
                'contextId' => contextId,
                'nodePathAndAttributes' => itemNodeUpdates
            };
            
            //Step 6 - Update context
            System.debug('--- PREHOOK: SUBMITTING CONTEXT UPDATE ---');
            System.debug(JSON.serializePretty(updateInput));
            industriesContext.updateContextAttributes(updateInput);
        }

        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        response.status = RevSignaling.TransactionStatus.SUCCESS;
        return response;
    }
}

IMPORTANT To add custom field information to Asset State Period and Asset Action Source, create appropriate cross-context mappings.
