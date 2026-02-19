global class serviceContractQuote{
//see https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_placequote_GraphRequest.htm
    @InvocableMethod(label='Create Service Contract Quote' description='Creates a service contract quote and returns the quote id' category='Quote')
    public static List<String> createUpdateQuote(List<svcContractRequest> svcContractRequests){
        List<Id> myAssetIds = new List<Id>();
        for(sObject myObject : svcContractRequests[0].assets){
            myAssetIds.add(myObject.Id);
        }
        
        List<Contact> quoteContacts = [SELECT Id, Name FROM Contact LIMIT 1];
        String contactId = quoteContacts[0].Id;
        
        List<Asset> myAssets = new List<Asset>();
        myAssets=[SELECT Id, AccountId FROM Asset WHERE Id in :myAssetIds];
        //System.debug('========0=======');
        List<String> myIds=new List<String>();
        String productId=svcContractRequests[0].productId;
        String priceBookId=svcContractRequests[0].priceBookId;
        String priceBookEntryId=svcContractRequests[0].priceBookEntryId;
        String productRelationshipTypeId=svcContractRequests[0].productRelationshipTypeId;
        //System.debug('========1======='+productId);
        //get options
        List<ProductRelatedComponent> options = [SELECT Id, Quantity, ChildProductId FROM ProductRelatedComponent WHERE ParentProductId=:productId AND IsComponentRequired=TRUE];
        List<Id> optionIds = new List<Id>();
        for(ProductRelatedComponent myPRC : options){
            System.debug('CHILD======='+myPRC.ChildProductId);
            optionIds.add(myPRC.ChildProductId);
        }
        //System.debug('========2=======');
        //get PBEs for options
        List<PriceBookEntry> pbes = [SELECT Id,Product2Id  FROM PriceBookEntry WHERE Product2Id in :optionIds AND Pricebook2Id=:priceBookId];
        Map<String,String> optionPBEs = new Map<String, String>();
        for(PriceBookEntry pbe : pbes){
            optionPBEs.put(pbe.Product2Id, pbe.Id);
        }
        //System.debug('========3=======');
        //Quote Setup
        PlaceQuote.RecordResource quoteRecord = new PlaceQuote.RecordResource(Quote.getSobjectType(),'POST');
        //PlaceQuote.RecordResource quoteRecord = new PlaceQuote.RecordResource(Quote.getSobjectType(),'PATCH',qId);
        Map<String,Object> quoteFieldValues = new Map<String,Object>();
        //quoteFieldValues.put('Id',qId);
        //quoteFieldValues.put('CalculationStatus','NotStarted');
       
        quoteFieldValues.put('Name','Service Contract Quote');
        
        quoteFieldValues.put('BillToContactId',contactId);
        quoteFieldValues.put('ContactId',contactId);
        quoteFieldValues.put('BillingStreet','415 Mission St');
        quoteFieldValues.put('BillingCity','San Francisco');
        quoteFieldValues.put('BillingPostalCode','94105');
        quoteFieldValues.put('BillingCountry','USA');
        quoteFieldValues.put('ShippingStreet','415 Mission St');
        quoteFieldValues.put('ShippingCity','San Francisco');
        quoteFieldValues.put('ShippingPostalCode','94105');
        quoteFieldValues.put('ShippingCountry','USA');
       
        //quoteFieldValues.put('OpportunityId','0061Q000012RlcfQAC');
        quoteFieldValues.put('QuoteAccountId',myAssets[0].AccountId);
        //quoteFieldValues.put('Pricebook2Id','01sa5000001R7T3AAK');
        quoteFieldValues.put('Pricebook2Id',priceBookId);
        quoteRecord.fieldValues = quoteFieldValues;
        PlaceQuote.RecordWithReferenceRequest quoteItemRecords = new PlaceQuote.RecordWithReferenceRequest('refQuote',quoteRecord);
        List<PlaceQuote.RecordWithReferenceRequest> listOfRecords = new List<PlaceQuote.RecordWithReferenceRequest>();
        listOfRecords.add(quoteItemRecords);
        //System.debug('========4=======');
        
        Date todaysDate = Date.today();
        Date startDate = todaysDate.addDays(10);
        Date endDate = todaysDate.addDays(374);
        String startDateStr = String.valueOf(startDate);
        String endDateStr = String.valueOf(endDate);
        
        integer counter=0;
        for(Asset myAsset : myAssets){
            //System.debug('========5======='+counter);
            counter++;
            //Quote Line Set-up
            PlaceQuote.RecordResource quoteLineItemRecord1 = new PlaceQuote.RecordResource(QuoteLineItem.getSobjectType(),'POST');
            Map<String,Object> quoteLineItemFieldValues = new Map<String,Object>();
            quoteLineItemFieldValues.put('Product2Id',productId);
            //quoteLineItemFieldValues.put('Product2Id','01tWt000002V0IjIAK');
            quoteLineItemFieldValues.put('PricebookEntryId',priceBookEntryId);
            //quoteLineItemFieldValues.put('PricebookEntryId','01uWt000000crBNIAY');
            quoteLineItemFieldValues.put('Quantity','1.0');
            quoteLineItemFieldValues.put('Covered_Asset__c',myAsset.Id);
            //quoteLineItemFieldValues.put('UnitPrice','15.0');
            //quoteLineItemFieldValues.put('StartDate','2024-09-01');
            //quoteLineItemFieldValues.put('EndDate','2025-08-31');
            quoteLineItemFieldValues.put('StartDate',startDateStr);
            quoteLineItemFieldValues.put('EndDate',endDateStr);
            quoteLineItemFieldValues.put('PeriodBoundary','Anniversary');
            quoteLineItemFieldValues.put('BillingFrequency','Annual');
            quoteLineItemFieldValues.put('QuoteId','@{refQuote.id}');
            quoteLineItemRecord1.fieldValues = quoteLineItemFieldValues;
            
            PlaceQuote.RecordWithReferenceRequest quoteLineItemRecords1 = new PlaceQuote.RecordWithReferenceRequest('refQuoteItem1_'+counter,quoteLineItemRecord1);
            listOfRecords.add(quoteLineItemRecords1);
            //System.debug('========6======='+counter);
            //Quote OPTIONS Line Set-up
            integer countOption = 0;
            for(ProductRelatedComponent myPRC : options){
                countOption++;
                //System.debug('========7======='+counter+'>'+countOption);
                PlaceQuote.RecordResource quoteLineItemRecord2 = new PlaceQuote.RecordResource(QuoteLineItem.getSobjectType(),'POST');
                Map<String,Object> quoteLineItemFieldValues2 = new Map<String,Object>();
                quoteLineItemFieldValues2.put('Product2Id',myPRC.ChildProductId);
                quoteLineItemFieldValues2.put('PricebookEntryId',optionPBEs.get(myPRC.ChildProductId));
                quoteLineItemFieldValues2.put('Quantity','1.0');
                quoteLineItemFieldValues2.put('Covered_Asset__c',myAsset.Id);
                //quoteLineItemFieldValues.put('UnitPrice','15.0');
                //quoteLineItemFieldValues2.put('StartDate','2024-09-01');
                //quoteLineItemFieldValues2.put('EndDate','2025-08-31');
                quoteLineItemFieldValues2.put('StartDate',startDateStr);
                quoteLineItemFieldValues2.put('EndDate',endDateStr);
                quoteLineItemFieldValues2.put('PeriodBoundary','Anniversary');
                quoteLineItemFieldValues2.put('BillingFrequency','Annual');
                quoteLineItemFieldValues2.put('QuoteId','@{refQuote.id}');
                quoteLineItemRecord2.fieldValues = quoteLineItemFieldValues2;
                //System.debug('========8======='+counter+'>'+countOption);
                PlaceQuote.RecordWithReferenceRequest quoteLineItemRecords2 = new PlaceQuote.RecordWithReferenceRequest('refQuoteItem_'+counter+'_'+countOption,quoteLineItemRecord2);
                //System.debug('========9======='+counter+'>'+countOption);
            
                //QLR
                // Create Quote Line Relationship
                PlaceQuote.RecordResource qlr1 = new PlaceQuote.RecordResource(QuoteLineRelationship.getSobjectType(),'POST');
                Map<String,Object> qlrFields = new Map<String,Object>();
                qlrFields.put('ProductRelationshipTypeId', productRelationshipTypeId);
                qlrFields.put('ProductRelatedComponentId', myPRC.Id);
                qlrFields.put('MainQuoteLineId', '@{refQuoteItem1_'+counter+'.id}');
                qlrFields.put('AssociatedQuoteLineId', '@{refQuoteItem_'+counter+'_'+countOption+'.id}');
                qlrFields.put('AssociatedQuoteLinePricing', 'IncludedInBundlePrice');
                qlr1.fieldValues = qlrFields;
                //System.debug('========10======='+counter+'>'+countOption);
                PlaceQuote.RecordWithReferenceRequest qlr = new PlaceQuote.RecordWithReferenceRequest('QuoteLineRelationship_'+counter+'_'+countOption, qlr1);
                //System.debug('========11======='+counter+'>'+countOption);
                listOfRecords.add(quoteLineItemRecords2);
                //System.debug('========12======='+counter+'>'+countOption);
                listOfRecords.add(qlr);
                //System.debug('========13======='+counter+'>'+countOption);
             }
        }
           
        //System.debug('========14=======');
        
        //execute
        PlaceQuote.GraphRequest graph = new PlaceQuote.GraphRequest('test',listOfRecords);
        PlaceQuote.ConfigurationOptionsInput cInput = new PlaceQuote.ConfigurationOptionsInput();
        cInput.validateProductCatalog=false;
        cInput.validateAmendRenewCancel=false;
        cInput.executeConfigurationRules=false;
        cInput.addDefaultConfiguration=false;
        
        System.debug(graph);
        System.debug(cInput);
        //System.debug('========15=======');
        //Place Quote Call
        //PlaceQuote.PlaceQuoteResponse resp = PlaceQuote.PlaceQuoteRLMApexProcessor.execute(PlaceQuote.PricingPreferenceEnum.System,graph, PlaceQuote.ConfigurationInputEnum.RunAndAllowErrors,cInput);
        PlaceQuote.PlaceQuoteResponse resp = PlaceQuote.PlaceQuoteRLMApexProcessor.execute(PlaceQuote.PricingPreferenceEnum.System,graph, PlaceQuote.ConfigurationInputEnum.Skip,cInput);
        System.debug(resp);
        
        myIds.add(resp.quoteId);
        
        return myIds;
        
    }
    
    global class svcContractRequest {
        @InvocableVariable(required=true)
        global List<sObject> assets;
        
        @InvocableVariable(required=true)
        global String productId;
        
        @InvocableVariable(required=true)
        global String priceBookId;
        
        @InvocableVariable(required=true)
        global String priceBookEntryId;
        
        @InvocableVariable(required=true)
        global String productRelationshipTypeId;
        
        
    }
    

}