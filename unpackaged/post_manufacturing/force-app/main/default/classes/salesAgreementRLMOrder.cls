global class salesAgreementRLMOrder{
    //see https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_placequote_GraphRequest.htm
        @InvocableMethod(label='Create Order from Sales Agreement' description='Creates an order from the sales agreement' category='Order')
        public static List<String> createUpdateQuote(List<saProductListEntries> saProducts){


            List<SalesAgreementProductSchedule> mySAProductSchedules = new List<SalesAgreementProductSchedule>();
            mySAProductSchedules = saProducts[0].salesagreementProductSchedules;
            
            //System.debug('========0=======');
            List<String> myIds=new List<String>();
            
            string orderDateString = String.valueOf(saProducts[0].orderDate);
            /*
            //Order Setup
            List<CommerceOrders.RecordWithReferenceRequest> recordNodes = new List<CommerceOrders.RecordWithReferenceRequest>();
    
			// Prepare for the Order 
			Map<String,Object> orderFieldValues = new Map<String,Object>();
			orderFieldValues.put('AccountId',saProducts[0].customerAcctId);
			orderFieldValues.put('Pricebook2Id', saProducts[0].priceBookId);
			orderFieldValues.put('EffectiveDate', orderDateString);
            orderFieldValues.put('SalesAgreementId',saProducts[0].salesAgreementId);
            orderFieldValues.put('Status','Draft');
            
            //create record object
            CommerceOrders.RecordResource orderRecord = new CommerceOrders.RecordResource(Order.getSobjectType(), 'POST');
			orderRecord.fieldValues = orderFieldValues;
            system.debug('ORDER DEBUG BELOW');
            system.debug(orderRecord);
            
            //create order lines & app usage
            
            CommerceOrders.RecordWithReferenceRequest orderRecordNode = new CommerceOrders.RecordWithReferenceRequest('refOrder', orderRecord);
			recordNodes.add(orderRecordNode);

			// Prepare for the App Usage Assignment
			Map<String,Object> auaFieldValues = new Map<String,Object>();
			auaFieldValues.put('AppUsageType', 'RevenueLifecycleManagement');
			auaFieldValues.put('RecordId', '@{refOrder.id}');

			CommerceOrders.RecordResource auaRecord = new CommerceOrders.RecordResource(AppUsageAssignment.getSobjectType(), 'POST');
			auaRecord.fieldValues = auaFieldValues;

			CommerceOrders.RecordWithReferenceRequest auaRecordNode = new CommerceOrders.RecordWithReferenceRequest('refAppTag', auaRecord);
			recordNodes.add(auaRecordNode);

			// Prepare for the Order Item
			
            integer counter=0;
            for(SalesAgreementProductSchedule mySAProductSchedule : mySAProductSchedules){
            	counter++;
				Map<String,Object> oiFieldValues = new Map<String,Object>();
				oiFieldValues.put('OrderId', '@{refOrder.id}');
				oiFieldValues.put('PricebookEntryId',mySAProductSchedule.PricebookEntryId__c);
				oiFieldValues.put('Product2Id',mySAProductSchedule.Product2Id__c);
				oiFieldValues.put('Quantity', mySAProductSchedule.PlannedQuantity);
				oiFieldValues.put('UnitPrice', mySAProductSchedule.SalesPrice);

				CommerceOrders.RecordResource oiRecord = new CommerceOrders.RecordResource(OrderItem.getSobjectType(), 'POST');
				oiRecord.fieldValues = oiFieldValues;

				CommerceOrders.RecordWithReferenceRequest oiRecordNode = new CommerceOrders.RecordWithReferenceRequest('refOrderItem_'+counter, oiRecord);
				recordNodes.add(oiRecordNode);
                system.debug('ORDER NODES BELOW');
                system.debug('record node here: '+ recordNodes);
            }
            
            
            CommerceOrders.PricingPreferenceEnum pricingPreference = CommerceOrders.PricingPreferenceEnum.System;
			CommerceOrders.CatalogRatesPreferenceEnum catalogRatesPreference = CommerceOrders.CatalogRatesPreferenceEnum.Skip;
			CommerceOrders.ConfigurationInputEnum configurationPreference = CommerceOrders.ConfigurationInputEnum.Skip;
			CommerceOrders.ConfigurationOptionsInput configurationInput = new CommerceOrders.ConfigurationOptionsInput();
			configurationInput.validateProductCatalog = false;
			configurationInput.validateAmendRenewCancel = false;
			configurationInput.executeConfigurationRules = false;
			configurationInput.addDefaultConfiguration = false;
            
            CommerceOrders.GraphRequest graph = new CommerceOrders.GraphRequest('testGraph', recordNodes);
            CommerceOrders.PlaceOrderResult result = CommerceOrders.PlaceOrderExecutor.execute(graph, pricingPreference, catalogRatesPreference, configurationPreference, configurationInput);
            
            
            // Process any error, if exists
            if (!result.success) {
              List<ConnectApi.PlaceOrderErrorResponse> errors = result.responseError;
              for (ConnectApi.PlaceOrderErrorResponse error : errors) {
                System.debug(error.errorCode + ': ' + error.message);
              }
            }
            */
            

            //Quote Setup
            PlaceQuote.RecordResource quoteRecord = new PlaceQuote.RecordResource(Quote.getSobjectType(),'POST');
            
            Map<String,Object> quoteFieldValues = new Map<String,Object>();

            quoteFieldValues.put('QuoteAccountId',saProducts[0].customerAcctId);
            quoteFieldValues.put('Name','Sales Agreement Quote');
            quoteFieldValues.put('Pricebook2Id',saProducts[0].priceBookId);
            quoteFieldValues.put('StartDate',orderDateString);
            quoteFieldValues.put('Sales_Agreement__c',saProducts[0].salesAgreementId);
            //quoteFieldValues.put('Status','Draft');
            quoteRecord.fieldValues = quoteFieldValues;
            PlaceQuote.RecordWithReferenceRequest quoteItemRecords = new PlaceQuote.RecordWithReferenceRequest('refQuote',quoteRecord);
            List<PlaceQuote.RecordWithReferenceRequest> listOfRecords = new List<PlaceQuote.RecordWithReferenceRequest>();
            listOfRecords.add(quoteItemRecords);
            //System.debug('========4=======');
            
            integer counter=0;
            for(SalesAgreementProductSchedule mySAProductSchedule : mySAProductSchedules){
                //System.debug('========5======='+counter);
                counter++;
                //Quote Line Set-up
                PlaceQuote.RecordResource quoteLineItemRecord1 = new PlaceQuote.RecordResource(QuoteLineItem.getSobjectType(),'POST');
                Map<String,Object> quoteLineItemFieldValues = new Map<String,Object>();
                quoteLineItemFieldValues.put('Product2Id',mySAProductSchedule.Product2Id__c);
                quoteLineItemFieldValues.put('PricebookEntryId',mySAProductSchedule.PricebookEntryId__c);
                quoteLineItemFieldValues.put('Quantity',mySAProductSchedule.PlannedQuantity);
                quoteLineItemFieldValues.put('StartDate',orderDateString);
                //quoteLineItemFieldValues.put('EndDate',orderDateString);
                quoteLineItemFieldValues.put('QuoteId','@{refQuote.id}');
                quoteLineItemRecord1.fieldValues = quoteLineItemFieldValues;
                
                PlaceQuote.RecordWithReferenceRequest quoteLineItemRecords1 = new PlaceQuote.RecordWithReferenceRequest('refQuoteItem1_'+counter,quoteLineItemRecord1);
                listOfRecords.add(quoteLineItemRecords1);
                //System.debug('========6======='+counter);
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
        
        global class saProductListEntries {
            @InvocableVariable(required=true)
            global List<sObject> salesagreementProductSchedules;

            @InvocableVariable(required=true)
            global String priceBookId;

            @InvocableVariable(required=true)
            global String salesAgreementId;

            @InvocableVariable(required=true)
            global String customerAcctId;

            @InvocableVariable(required=true)
            global Date orderDate;  
        }
        
    
    }